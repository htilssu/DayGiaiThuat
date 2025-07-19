from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()


class AIChatAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "YOUR_DEFAULT_KEY"
        # Initialize LLM with newer API
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0.7)

    def chat(self, code: str, results: List[dict], title: str, user_message: Optional[str] = None, all_tests_passed: Optional[bool] = None) -> str:
        """
        Xử lý hội thoại AI cho phần chat giải thuật.
        Nếu user_message có thì trả lời hội thoại, nếu không thì đánh giá code/test.
        """
        try:
            if user_message:
                system_prompt = f"""Bạn là một giảng viên dạy thuật toán chuyên nghiệp và thân thiện.
                Nhiệm vụ của bạn là giao tiếp và hỗ trợ giải đáp thắc mắc của học viên.
                Hãy trả lời một cách ngắn gọn, dễ hiểu và thân thiện.

                Context bài tập: {title}
                Code của học viên: {code[:200]}...
                Kết quả test: {results}"""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]

                response = self.llm.invoke(messages)
                return response.content
            else:
                # Đánh giá code/test dựa trên kết quả
                if all_tests_passed:
                    system_prompt = """Bạn là một chuyên gia giải thuật chuyên nghiệp, dễ thương và thân thiện.
                    Nhiệm vụ của bạn là đưa ra đánh giá cho học viên về cách giải thuật của họ và gợi ý cách tối ưu hơn.
                    Hãy đưa ra đánh giá thật ngắn gọn, dễ hiểu."""

                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=f"Đây là code của học viên: {code[:200]}... và đây là kết quả test: {results}. Context bài tập: {title}")
                    ]

                    response = self.llm.invoke(messages)
                    return response.content
                else:
                    failed_tests = [r for r in results if not r.get('passed', False)]
                    if failed_tests:
                        system_prompt = """Bạn là một chuyên gia giải thuật chuyên nghiệp, dễ thương và thân thiện.
                        Nhiệm vụ của bạn là đưa ra gợi ý cho học viên nếu họ làm bài chưa đúng và khen họ nếu họ đã đúng.
                        Hãy đưa ra gợi ý thật ngắn gọn, dễ hiểu và có chút chăm chọc.
                        Hãy chỉ đưa ra gợi ý về cách giải, không đưa ra lời giải cụ thể."""

                        messages = [
                            SystemMessage(content=system_prompt),
                            HumanMessage(content=f"Đây là code của học viên: {code[:200]}... và đây là kết quả test: {results}. Context bài tập: {title}")
                        ]

                        response = self.llm.invoke(messages)
                        return response.content
                    else:
                        return "💡 Code của bạn gần đúng rồi! Hãy kiểm tra lại một chút về format output hoặc xử lý edge cases."
        except Exception as e:
            print(f"Error in AI chat: {e}")
            # Fallback response
            if user_message:
                return f"Xin lỗi, tôi đang gặp sự cố kỹ thuật. Bạn hỏi: '{user_message}'. Hãy thử lại sau nhé!"
            else:
                return "Có lỗi xảy ra khi đánh giá code. Vui lòng thử lại sau."
