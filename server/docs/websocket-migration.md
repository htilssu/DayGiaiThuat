# WebSocket Migration for Test Answer Submission

## Overview

Hệ thống đã được chuyển đổi từ việc sử dụng HTTP requests sang WebSocket để cập nhật câu trả lời trong bài kiểm tra. Điều này mang lại:

- **Real-time updates**: Câu trả lời được lưu ngay lập tức khi người dùng chọn/nhập
- **Better performance**: Giảm số lượng HTTP requests
- **Auto-sync**: Tự động đồng bộ trạng thái khi kết nối được khôi phục
- **Smart debouncing**: Debounce cho essay questions, instant cho multiple choice

## Technical Changes

### Frontend Changes

#### 1. `useTestSession.ts`

- ✅ **Removed**: `submitAnswerMutation` với HTTP request
- ✅ **Added**: WebSocket connection với auto-reconnect
- ✅ **Added**: `sendAnswerViaSocket()` function
- ✅ **Added**: Smart debouncing logic cho essay questions
- ✅ **Changed**: `submitAnswer` từ async thành synchronous function
- ✅ **Added**: `connectionStatus` state để theo dõi trạng thái kết nối
- ✅ **Added**: `options.immediate` parameter để force immediate submission

#### 2. `testApi.ts`

- ✅ **Removed**: `SubmitSessionAnswerRequest` interface
- ✅ **Removed**: `submitSessionAnswer` function (không tồn tại)
- ✅ **Kept**: `connectToTestSession()` for WebSocket connection

#### 3. Components

- ✅ **TestPageNew.tsx**: Không cần thay đổi (chỉ truyền callback)
- ✅ **TestQuiz.tsx**: Updated interface để hỗ trợ options parameter
- ✅ **TestPage.tsx**: Đã có WebSocket implementation sẵn
- ✅ **ProblemQuestion.tsx**: Removed component-level debounce, simplified UI

### Backend (Already Implemented)

#### WebSocket Endpoint

```
/tests/ws/test-sessions/{session_id}
```

#### Supported Message Types

**Client to Server:**

```json
{
  "type": "save_answer",
  "question_id": "string",
  "answer": {
    "selectedOptionId": "string", // for multiple choice
    "code": "string" // for essay questions
  }
}
```

**Server to Client:**

```json
{
  "type": "answer_saved",
  "question_id": "string",
  "timestamp": "ISO_datetime"
}
```

## How It Works

### Smart Answer Submission Flow

#### Multiple Choice Questions

1. **User Clicks**: Người dùng chọn đáp án
2. **Instant Send**: Gửi ngay lập tức qua WebSocket (không debounce)
3. **Server Response**: Server confirm đã lưu

#### Essay Questions

1. **User Types**: Người dùng gõ câu trả lời
2. **Local Update**: State local được cập nhật ngay lập tức
3. **Debounce**: Chờ 1.5 giây kể từ lần gõ cuối
4. **WebSocket Send**: Gửi answer qua WebSocket
5. **Server Response**: Server confirm đã lưu

#### Force Immediate Submission

```typescript
// For immediate submission (bypass debounce)
submitAnswer(questionId, answer, { immediate: true });
```

**Use Cases for Immediate Submission:**

- User clicks "Save Draft" button cho essay questions
- Auto-save trước khi chuyển sang câu hỏi khác
- Final submission preparation
- Recovery từ network disconnection

**Example Implementation:**

```typescript
// In TestQuiz component
const handleNextQuestion = () => {
  // Force save current answer before moving to next question
  const currentQuestion = getCurrentQuestion();
  const currentAnswer = answers[currentQuestion.id];

  if (currentAnswer && currentQuestion.type === "essay") {
    onSubmitAnswer(currentQuestion.id, currentAnswer, { immediate: true });
  }

  onNextQuestion();
};
```

### Debounce Logic Details

```typescript
// In useTestSession.ts
const submitAnswer = useCallback(
  (
    questionId: string,
    answer: TestAnswer,
    options?: { immediate?: boolean }
  ) => {
    // Always update local state immediately
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));

    const questionType = getQuestionType(questionId);
    const immediate = options?.immediate || false;

    // Clear existing debounce for this question
    if (debounceTimeouts.current[questionId]) {
      clearTimeout(debounceTimeouts.current[questionId]);
      delete debounceTimeouts.current[questionId];
    }

    if (immediate || questionType === "single_choice") {
      // Send immediately
      sendAnswerViaSocket(questionId, answer);
    } else if (questionType === "essay") {
      // Debounce for 1.5 seconds
      debounceTimeouts.current[questionId] = setTimeout(() => {
        sendAnswerViaSocket(questionId, answer);
        delete debounceTimeouts.current[questionId];
      }, 1500);
    }
  },
  [sendAnswerViaSocket, getQuestionType]
);
```

### Auto-Reconnection

- Tự động reconnect sau 3 giây nếu connection bị mất
- Sync state khi kết nối được khôi phục
- Hiển thị connection status cho user

### Final Test Submission

- Clear tất cả pending debounce timeouts
- Send tất cả answers ngay lập tức
- Wait 500ms để đảm bảo tất cả messages được gửi
- Submit test qua HTTP

### Fallback Strategy

- Nếu WebSocket không hoạt động, vẫn có thể submit toàn bộ bài test cuối cùng qua HTTP
- Local state vẫn được maintain để không mất dữ liệu

## Testing

### Manual Testing

1. **Multiple Choice**: Click đáp án → check logs cho instant submission
2. **Essay Questions**: Gõ text → check logs cho debounced submission
3. **Mixed Questions**: Test chuyển đổi giữa các loại câu hỏi
4. **Network Issues**: Disconnect internet, check reconnection
5. **Final Submission**: Submit toàn bộ bài test

### Console Logs

Tìm các log sau trong browser console:

- `📤 Sending answer via WebSocket:` (instant cho multiple choice)
- `⏱️ Debouncing essay answer for question:` (essay questions)
- `✅ Answer saved:` (server confirmation)
- `⚠️ WebSocket not connected, cannot save answer`
- `WebSocket connected`
- `Attempting to reconnect...`

## Migration Benefits

### For Users

- ✅ Instant feedback cho multiple choice questions
- ✅ Smart debouncing cho essay questions (không spam requests)
- ✅ Không lo mất dữ liệu khi network không ổn định
- ✅ Real-time connection status
- ✅ Improved performance

### For Developers

- ✅ Cleaner code architecture
- ✅ Reduced HTTP request overhead
- ✅ Better error handling
- ✅ Consistent with other real-time features
- ✅ Centralized debounce logic

## Performance Characteristics

### Request Patterns

#### Before (HTTP-based)

- Multiple choice: 1 HTTP request per selection
- Essay: 1 HTTP request per keystroke (without debounce) or per debounce timeout
- Total: High HTTP overhead

#### After (WebSocket-based)

- Multiple choice: 1 WebSocket message per selection (instant)
- Essay: 1 WebSocket message per 1.5s debounce window
- Total: Minimal overhead, better UX

### Timing Configuration

- **Essay debounce**: 1.5 seconds (configurable)
- **Auto-reconnect**: 3 seconds
- **Final submission delay**: 500ms (to ensure all messages sent)

## Future Enhancements

### Possible Improvements

- [ ] **Configurable debounce timing**: Admin setting cho debounce delay
- [ ] **Typing indicators**: Hiển thị khi user đang typing (cho essay questions)
- [ ] **Collaborative features**: Multiple students cùng làm bài (admin mode)
- [ ] **Advanced analytics**: Track time spent per question
- [ ] **Offline support**: Cache answers locally khi offline
- [ ] **Progress indicators**: Visual feedback cho debounced saves

### Performance Monitoring

- [ ] Track WebSocket connection stability
- [ ] Monitor message delivery success rate
- [ ] Measure response time for answer saves
- [ ] Track debounce effectiveness (reduction in messages)
