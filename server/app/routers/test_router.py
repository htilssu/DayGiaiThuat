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
import asyncio

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
    TestHistorySummary,
)
from app.utils.utils import get_current_user


router = APIRouter(prefix="/tests", tags=["tests"])

# Kết nối WebSocket để theo dõi và cập nhật phiên làm bài
active_connections: Dict[str, WebSocket] = {}  # {session_id: websocket}
session_timers: Dict[str, asyncio.Task] = {}  # {session_id: timer_task}


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
    session_id: str,
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


@router.get("/sessions/history", response_model=List[TestHistorySummary])
async def get_test_history(
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy lịch sử làm bài kiểm tra của người dùng - chỉ thông tin cơ bản"""
    return await test_service.get_user_test_history(current_user.id)


@router.get("/sessions/{session_id}/detail", response_model=Dict[str, Any])
async def get_test_session_detail(
    session_id: str,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Lấy thông tin chi tiết của một phiên làm bài đã hoàn thành"""
    return await test_service.get_test_session_detail(session_id, current_user.id)


@router.put("/sessions/{session_id}", response_model=TestSessionRead)
async def update_test_session(
    session_id: str,
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
    session_id: str,
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
    session_id: str,
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


@router.websocket("/ws/test-sessions/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    test_service: TestService = Depends(get_test_service),
):
    """WebSocket endpoint để theo dõi và cập nhật phiên làm bài với timer tự động"""
    await websocket.accept()

    try:
        # Lấy thông tin session trước tiên
        session = await test_service.get_test_session(session_id)
        if not session:
            await websocket.send_json(
                {"type": "error", "message": "Không tìm thấy phiên làm bài"}
            )
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Kiểm tra nếu session đã hoàn thành
        if session.status in ["completed", "expired"]:
            await websocket.send_json(
                {
                    "type": "test_completed",
                    "status": session.status,
                    "message": "Bài kiểm tra đã hoàn thành",
                }
            )
            await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
            return

        # Lưu kết nối
        active_connections[session_id] = websocket

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

        # Bắt đầu timer nếu chưa có
        if session_id not in session_timers and session.time_remaining_seconds > 0:
            session_timers[session_id] = asyncio.create_task(
                monitor_session_timer(session_id, test_service)
            )

        # Lắng nghe cập nhật từ client
        while True:
            try:
                data = await websocket.receive_json()

                # Xử lý các loại tin nhắn
                if data["type"] == "heartbeat" or data["type"] == "ping":
                    # Gửi pong response
                    await websocket.send_json({"type": "pong"})

                elif data["type"] == "save_answer":
                    # Lưu câu trả lời
                    question_id = data.get("question_id")
                    answer = data.get("answer")
                    if question_id and answer is not None:
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

                elif data["type"] == "updateQuestionIndex":
                    # Cập nhật chỉ số câu hỏi hiện tại
                    new_index = data.get("questionIndex")
                    if new_index is not None:
                        update_data = TestSessionUpdate(
                            current_question_index=new_index
                        )
                        await test_service.update_session(session_id, update_data)
                        await websocket.send_json(
                            {
                                "type": "questionIndexUpdated",
                                "questionIndex": new_index,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                elif data["type"] == "sync":
                    # Đồng bộ trạng thái từ client
                    current_question_index = data.get("currentQuestionIndex")
                    answers = data.get("answers")

                    updates = {}
                    if current_question_index is not None:
                        updates["current_question_index"] = current_question_index
                    if answers:
                        # Merge với answers hiện tại
                        current_session = await test_service.get_test_session(
                            session_id
                        )
                        current_answers = current_session.answers or {}
                        current_answers.update(answers)
                        updates["answers"] = current_answers

                    if updates:
                        update_data = TestSessionUpdate(**updates)
                        await test_service.update_session(session_id, update_data)

            except ValueError:
                # Lỗi parsing JSON, gửi thông báo lỗi
                await websocket.send_json(
                    {"type": "error", "message": "Dữ liệu không hợp lệ"}
                )

    except WebSocketDisconnect:
        # Client đã disconnect
        pass
    except Exception as e:
        # Log lỗi
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup khi client ngắt kết nối
        if session_id in active_connections:
            del active_connections[session_id]


async def monitor_session_timer(session_id: str, test_service: TestService):
    """Theo dõi thời gian còn lại của session và tự động nộp bài khi hết thời gian"""
    try:
        while True:
            # Kiểm tra session mỗi 10 giây
            await asyncio.sleep(10)

            session = await test_service.get_test_session(session_id)
            if not session or session.status in ["completed", "expired"]:
                break

            # Tính thời gian còn lại
            elapsed_seconds = (datetime.utcnow() - session.start_time).total_seconds()
            remaining_time = max(
                0, session.time_remaining_seconds - int(elapsed_seconds)
            )

            # Cập nhật time_remaining_seconds trong database
            await test_service.update_session(
                session_id, TestSessionUpdate(time_remaining_seconds=remaining_time)
            )

            # Gửi cập nhật thời gian qua WebSocket
            if session_id in active_connections:
                try:
                    await active_connections[session_id].send_json(
                        {
                            "type": "timer_update",
                            "time_remaining_seconds": remaining_time,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                except Exception:
                    # Kết nối bị lỗi, dừng timer
                    break

            # Nếu hết thời gian, tự động nộp bài
            if remaining_time <= 0:
                await auto_submit_session(session_id, test_service)
                break

    except asyncio.CancelledError:
        # Timer bị hủy
        pass
    except Exception as e:
        print(f"Timer monitoring error for session {session_id}: {e}")
    finally:
        # Cleanup timer
        if session_id in session_timers:
            del session_timers[session_id]


async def auto_submit_session(session_id: str, test_service: TestService):
    """Tự động nộp bài khi hết thời gian"""
    try:
        session = await test_service.get_test_session(session_id)
        if not session or session.status in ["completed", "expired"]:
            return

        # Tự động nộp bài với câu trả lời hiện có
        submission = TestSubmission(answers=session.answers or {})
        result = await test_service.submit_test_session(
            session_id, submission, is_auto_submit=True
        )

        # Gửi thông báo hết thời gian qua WebSocket
        if session_id in active_connections:
            try:
                await active_connections[session_id].send_json(
                    {
                        "type": "time_expired",
                        "message": "Hết thời gian làm bài, bài kiểm tra đã được nộp tự động",
                        "result": {
                            "score": result.score,
                            "total_questions": result.total_questions,
                            "correct_answers": result.correct_answers,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            except Exception:
                pass

    except Exception as e:
        print(f"Auto submit error for session {session_id}: {e}")


async def broadcast_session_update(
    user_id: int, session_id: str, message: Dict[str, Any]
):
    """Gửi cập nhật đến WebSocket connection của phiên làm bài"""
    if session_id in active_connections:
        try:
            await active_connections[session_id].send_json(message)
        except Exception:
            # Xóa kết nối nếu không thể gửi
            if session_id in active_connections:
                del active_connections[session_id]


@router.get("/{test_id}/resume", response_model=Optional[TestSessionWithTest])
async def resume_test_session(
    test_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Kiểm tra và khôi phục phiên làm bài hiện có cho bài kiểm tra"""
    # Tìm phiên làm bài đang hoạt động cho bài kiểm tra này
    active_session = await test_service.get_active_session(current_user.id, test_id)

    if not active_session:
        return None

    # Kiểm tra quyền truy cập
    access_check = await test_service.can_access_test_session(
        active_session.id, current_user.id
    )

    if not access_check["can_access"]:
        return None

    # Lấy thông tin bài kiểm tra
    test = await test_service.get_test(test_id)
    if not test:
        return None

    # Trả về session với thông tin bài kiểm tra
    return {**active_session.__dict__, "test": test}


@router.get("/{test_id}/can-take")
async def can_take_test(
    test_id: int,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Kiểm tra xem người dùng có thể làm bài kiểm tra hay không"""
    # Kiểm tra xem bài kiểm tra có tồn tại không
    test = await test_service.get_test(test_id)
    if not test:
        return {
            "can_take": False,
            "reason": "test_not_found",
            "message": "Không tìm thấy bài kiểm tra",
        }

    # Kiểm tra phiên làm bài hiện có
    active_session = await test_service.get_active_session(current_user.id, test_id)

    if active_session:
        access_check = await test_service.can_access_test_session(
            active_session.id, current_user.id
        )
        if access_check["can_access"]:
            return {
                "can_take": True,
                "has_active_session": True,
                "session_id": active_session.id,
                "message": "Có phiên làm bài đang hoạt động",
            }
        else:
            return {
                "can_take": False,
                "reason": access_check["reason"],
                "message": access_check["message"],
            }

    return {
        "can_take": True,
        "has_active_session": False,
        "message": "Có thể bắt đầu làm bài kiểm tra",
    }


@router.get("/sessions/{session_id}/access-check")
async def check_session_access(
    session_id: str,
    test_service: TestService = Depends(get_test_service),
    current_user=Depends(get_current_user),
):
    """Kiểm tra quyền truy cập phiên làm bài"""
    access_check = await test_service.can_access_test_session(
        session_id, current_user.id
    )
    return access_check
