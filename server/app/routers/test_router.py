from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.services.test_service import TestService, get_test_service
from app.schemas.test_schema import (
    TestCreate,
    TestUpdate,
    TestRead,
    TestSessionCreate,
    TestSessionUpdate,
    TestSessionRead,
    TestSessionWithTest,
    TestSubmission,
    TestResult,
)
from app.utils.utils import get_current_user

router = APIRouter(prefix="/tests", tags=["tests"])

# Kết nối WebSocket để theo dõi và cập nhật phiên làm bài
active_connections: Dict[int, Dict[int, WebSocket]] = (
    {}
)  # {user_id: {session_id: websocket}}


@router.get("/", response_model=List[TestRead])
async def get_all_tests(
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy danh sách tất cả các bài kiểm tra"""
    tests = await test_service.get_all_tests()
    return tests


@router.get("/topic/{topic_id}", response_model=List[TestRead])
async def get_tests_by_topic(
    topic_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy danh sách bài kiểm tra theo topic"""
    tests = await test_service.get_tests_by_topic(topic_id)
    return tests


@router.get("/{test_id}", response_model=TestRead)
async def get_test(
    test_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy thông tin chi tiết của một bài kiểm tra"""
    test = await test_service.get_test(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài kiểm tra"
        )
    return test


@router.post("/", response_model=TestRead, status_code=status.HTTP_201_CREATED)
async def create_test(
    test_data: TestCreate,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Tạo một bài kiểm tra mới (chỉ dành cho admin)"""
    # Kiểm tra quyền admin (thêm logic sau)
    test = await test_service.create_test(test_data)
    return test


@router.put("/{test_id}", response_model=TestRead)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Cập nhật thông tin bài kiểm tra (chỉ dành cho admin)"""
    # Kiểm tra quyền admin (thêm logic sau)
    test = await test_service.update_test(test_id, test_data)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài kiểm tra"
        )
    return test


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Xóa bài kiểm tra (chỉ dành cho admin)"""
    # Kiểm tra quyền admin (thêm logic sau)
    success = await test_service.delete_test(test_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài kiểm tra"
        )
    return None


@router.post(
    "/sessions", response_model=TestSessionRead, status_code=status.HTTP_201_CREATED
)
async def create_test_session(
    session_data: TestSessionCreate,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Tạo một phiên làm bài kiểm tra mới"""
    # Đảm bảo người dùng chỉ tạo phiên cho chính họ
    if session_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền tạo phiên làm bài cho người dùng khác",
        )

    session = await test_service.create_test_session(session_data)
    return session


@router.post(
    "/sessions/from-topic/{topic_id}",
    response_model=TestSessionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_session_from_topic(
    topic_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Tạo một phiên làm bài kiểm tra mới từ một topic"""
    session = await test_service.create_test_session_from_topic(
        topic_id, current_user.id
    )
    return session


@router.get("/sessions/{session_id}", response_model=TestSessionWithTest)
async def get_test_session(
    session_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy thông tin chi tiết của một phiên làm bài"""
    session = await test_service.get_test_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên làm bài"
        )

    # Đảm bảo người dùng chỉ xem phiên của chính họ
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xem phiên làm bài của người dùng khác",
        )

    # Lấy thêm thông tin bài kiểm tra
    test = await test_service.get_test(session.test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài kiểm tra liên quan",
        )

    # Kết hợp thông tin
    return {**session.__dict__, "test": test}


@router.get("/sessions/user/me", response_model=List[TestSessionRead])
async def get_my_test_sessions(
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy danh sách các phiên làm bài của người dùng hiện tại"""
    sessions = await test_service.get_user_sessions(current_user.id)
    return sessions


@router.put("/sessions/{session_id}", response_model=TestSessionRead)
async def update_test_session(
    session_id: int,
    update_data: TestSessionUpdate,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Cập nhật thông tin phiên làm bài"""
    # Kiểm tra quyền truy cập
    session = await test_service.get_test_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên làm bài"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật phiên làm bài của người dùng khác",
        )

    updated_session = await test_service.update_session(session_id, update_data)
    return updated_session


@router.post(
    "/sessions/{session_id}/answers/{question_id}", response_model=TestSessionRead
)
async def submit_answer(
    session_id: int,
    question_id: str,
    answer: Dict[str, Any],
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Nộp câu trả lời cho một câu hỏi trong phiên làm bài"""
    # Kiểm tra quyền truy cập
    session = await test_service.get_test_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên làm bài"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật phiên làm bài của người dùng khác",
        )

    updated_session = await test_service.update_session_answer(
        session_id, question_id, answer
    )

    # Gửi cập nhật qua WebSocket nếu có kết nối
    await broadcast_session_update(
        session.user_id,
        session_id,
        {
            "type": "answer_update",
            "question_id": question_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    return updated_session


@router.post("/sessions/{session_id}/submit", response_model=TestResult)
async def submit_test(
    session_id: int,
    submission: Optional[TestSubmission] = None,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Nộp bài kiểm tra và nhận kết quả"""
    # Kiểm tra quyền truy cập
    session = await test_service.get_test_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên làm bài"
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền nộp bài kiểm tra của người dùng khác",
        )

    result = await test_service.submit_test_session(session_id, submission)

    # Gửi thông báo qua WebSocket
    await broadcast_session_update(
        session.user_id,
        session_id,
        {
            "type": "test_submitted",
            "timestamp": datetime.utcnow().isoformat(),
            "result": {
                "score": result.score,
                "total_questions": result.total_questions,
                "correct_answers": result.correct_answers,
            },
        },
    )

    return result


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """WebSocket endpoint để theo dõi và cập nhật phiên làm bài"""
    # Kiểm tra quyền truy cập
    session = await test_service.get_test_session(session_id)
    if not session or session.user_id != current_user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    # Lưu kết nối
    if current_user.id not in active_connections:
        active_connections[current_user.id] = {}
    active_connections[current_user.id][session_id] = websocket

    try:
        # Gửi trạng thái hiện tại của phiên
        await websocket.send_json(
            {
                "type": "session_state",
                "session_id": session_id,
                "current_question_index": session.current_question_index,
                "time_remaining_seconds": session.time_remaining_seconds,
                "answers": session.answers,
                "status": session.status,
            }
        )

        # Lắng nghe cập nhật từ client
        while True:
            data = await websocket.receive_json()

            # Xử lý các loại tin nhắn
            if data["type"] == "heartbeat":
                # Cập nhật thời gian hoạt động
                update_data = TestSessionUpdate(last_activity=datetime.utcnow())
                await test_service.update_session(session_id, update_data)

                # Gửi lại thời gian còn lại
                updated_session = await test_service.get_test_session(session_id)
                await websocket.send_json(
                    {
                        "type": "time_update",
                        "time_remaining_seconds": updated_session.time_remaining_seconds,
                    }
                )

            elif data["type"] == "save_answer":
                # Lưu câu trả lời
                question_id = data.get("question_id")
                answer = data.get("answer")
                if question_id and answer:
                    await test_service.update_session_answer(
                        session_id, question_id, answer
                    )
                    await websocket.send_json(
                        {
                            "type": "answer_saved",
                            "question_id": question_id,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

    except WebSocketDisconnect:
        # Xóa kết nối khi client ngắt kết nối
        if (
            current_user.id in active_connections
            and session_id in active_connections[current_user.id]
        ):
            del active_connections[current_user.id][session_id]
            if not active_connections[current_user.id]:
                del active_connections[current_user.id]


async def broadcast_session_update(
    user_id: int, session_id: int, message: Dict[str, Any]
):
    """Gửi cập nhật đến tất cả các kết nối WebSocket của phiên làm bài"""
    if user_id in active_connections and session_id in active_connections[user_id]:
        try:
            await active_connections[user_id][session_id].send_json(message)
        except Exception:
            # Xóa kết nối nếu không thể gửi
            del active_connections[user_id][session_id]
            if not active_connections[user_id]:
                del active_connections[user_id]
