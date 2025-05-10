import os
from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel as LangchainBaseModel, Field as LangchainField
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_pinecone import PineconeVectorStore

from app.core.config import settings


class TestCase(LangchainBaseModel):
    """
    Mô tả một trường hợp thử nghiệm cho bài toán giải thuật.

    Attributes:
        input_data (str): Dữ liệu đầu vào cho trường hợp thử nghiệm. Alias là "input".
        output_data (str): Kết quả đầu ra mong đợi. Alias là "output".
        explain (str): Giải thích cho trường hợp thử nghiệm.
    """
    input_data: str = LangchainField(..., alias="input", description="Dữ liệu đầu vào cho trường hợp thử nghiệm.")
    output_data: str = LangchainField(..., alias="output", description="Kết quả đầu ra mong đợi.")
    explain: str = LangchainField(..., description="Giải thích cho trường hợp thử nghiệm.")

class ExerciseDetail(LangchainBaseModel):
    """
    Mô tả chi tiết một bài tập giải thuật được tạo ra.

    Attributes:
        name (str): Tên của bài toán.
        description (str): Mô tả chi tiết về bài toán.
        constraints (Optional[str]): Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).
        suggest (Optional[str]): Gợi ý để giải bài toán.
        case (List[TestCase]): Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.
    """
    name: str = LangchainField(..., description="Tên của bài toán.")
    description: str = LangchainField(..., description="Mô tả chi tiết về bài toán.")
    constraints: Optional[str] = LangchainField(None, description="Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).")
    suggest: Optional[str] = LangchainField(None, description="Gợi ý để giải bài toán.")
    case: List[TestCase] = LangchainField(..., min_items=3, description="Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.")


# System prompt được lấy từ n8n workflow
SYSTEM_PROMPT_TEMPLATE = """Bạn là một AI agent chuyên tạo các bài tập giải thuật để người dùng luyện tập lập trình. Nhiệm vụ của bạn là tạo ra các đề bài rõ ràng, ngắn gọn và có ngữ cảnh đời thường, giúp người dùng dễ dàng liên hệ với các tình huống thực tế. Khi tạo một bài tập, hãy tuân theo mẫu sau:

Tên bài tập: [Tạo một tiêu đề mô tả cho bài tập, bao gồm ngữ cảnh đời thường nếu có thể]
Ngữ cảnh: [Cung cấp một tình huống đời thường liên quan đến bài tập, ví dụ: "Thư đang cần sắp xếp các cuốn sách trên kệ theo thứ tự từ nhỏ đến lớn."]
Mô tả: [Giải thích chi tiết về bài tập, bao gồm bất kỳ định nghĩa hoặc thông tin cần thiết nào để hiểu bài toán]
Đầu vào: [Xác định định dạng của dữ liệu đầu vào]
Đầu ra: [Xác định định dạng của dữ liệu đầu ra mong muốn]
Ví dụ (phải có 3 ví dụ đơn giản, dễ giải thích, nhưng không được trùng trường hợp nổi bật):
Đầu vào: [Cung cấp một ví dụ đầu vào]
Đầu ra: [Cung cấp đầu ra tương ứng]
Giải thích: [Cung cấp giải thích chi tiết ví dụ: đầu tiên i = 0 có giá trị bé hơn 1, chuyển nó ra phía trước...]

Ràng buộc: [Tùy chọn: xác định bất kỳ ràng buộc nào về dữ liệu đầu vào, chẳng hạn như phạm vi giá trị, giới hạn kích thước, v.v.]
Hãy đảm bảo rằng các bài tập bạn tạo ra đều logic, có thể giải được và phù hợp để luyện tập lập trình. Các bài tập nên bao quát nhiều chủ đề giải thuật khác nhau như mảng, chuỗi, tìm kiếm, sắp xếp, lập trình động, đồ thị và cây. Bạn cần tạo bài tập ở các mức độ khó khác nhau (dễ, trung bình, khó) theo yêu cầu của người dùng.

Khi tạo ngữ cảnh đời thường, hãy chọn các tình huống quen thuộc, chẳng hạn như quản lý danh sách công việc, sắp xếp hàng đợi, tính toán chi phí mua sắm, hoặc tổ chức dữ liệu trong các hoạt động hàng ngày. Ví dụ cụ thể như "Thư đang cần sắp xếp các cuốn sách trên kệ theo thứ tự từ nhỏ đến lớn" sẽ giúp người dùng dễ hình dung bài toán.

Nếu bài tập liên quan đến đồ thị hoặc cây, hãy mô tả rõ ràng cấu trúc bằng văn bản, bao gồm các nút, cạnh và thuộc tính liên quan.

Mục tiêu là tạo ra các bài tập hấp dẫn, mang tính giáo dục và thực tế, giúp người dùng cải thiện kỹ năng tư duy giải thuật và lập trình.

Hãy đảm bảo câu trả lời của bạn tuân thủ định dạng JSON được mô tả bởi schema sau:
{format_instructions}
"""

class GenerateExerciseQuestionAgent:
    """
    Một AI agent sử dụng Langchain để tạo ra các bài tập giải thuật.
    Agent này có khả năng sử dụng Google Gemini làm mô hình ngôn ngữ,
    truy vấn kiến thức từ Pinecone vector store (AlgoVault),
    quản lý lịch sử hội thoại với MongoDB, và trả về kết quả có cấu trúc.
    """
    def __init__(
        self,
        pinecone_index_name: str = "giaithuat",
        mongodb_db_name: str = "chat_history",
        mongodb_collection_name: str = "exercise_sessions",
        llm_model_name: str = "models/gemini-2.5-flash-preview-04-17", # Updated to a common flash model
        embedding_model_name: str = "models/text-embedding-004"
    ):
        """
        Khởi tạo GenerateExerciseQuestionAgent.

        Args:
            google_api_key (Optional[str]): API key cho Google AI Studio. Mặc định lấy từ biến môi trường GOOGLE_API_KEY.
            pinecone_api_key (Optional[str]): API key cho Pinecone. Mặc định lấy từ biến môi trường PINECONE_API_KEY.
            pinecone_environment (Optional[str]): Môi trường Pinecone. Mặc định lấy từ biến môi trường PINECONE_ENVIRONMENT.
            pinecone_index_name (str): Tên của Pinecone index. Mặc định là "giaithuat".
            mongodb_uri (Optional[str]): Connection URI cho MongoDB. Mặc định lấy từ biến môi trường MONGODB_URI.
            mongodb_db_name (str): Tên database MongoDB để lưu lịch sử chat. Mặc định là "chat_history".
            mongodb_collection_name (str): Tên collection MongoDB để lưu lịch sử chat. Mặc định là "exercise_sessions".
            llm_model_name (str): Tên model Gemini sẽ sử dụng. Mặc định là "models/gemini-1.5-flash-latest".
            embedding_model_name (str): Tên model embedding sẽ sử dụng. Mặc định là "models/text-embedding-004".

        Raises:
            ValueError: Nếu thiếu các API key hoặc thông tin cấu hình cần thiết.
        """
        self.google_api_key = settings.GOOGLE_API_KEY
        self.pinecone_api_key = settings.PINECONE_API_KEY
        self.pinecone_environment = settings.PINECONE_ENVIRONMENT
        self.mongodb_uri = settings.MONGO_URI

        if not self.google_api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass as argument.")
        if not self.pinecone_api_key or not self.pinecone_environment:
            raise ValueError("Pinecone API key and environment are required. Set PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables or pass as arguments.")
        if not self.mongodb_uri:
            raise ValueError("MongoDB URI is required. Set MONGODB_URI environment variable or pass as argument.")

        self.pinecone_index_name = settings.PINECONE_INDEX_NAME
        self.mongodb_db_name = settings.MONGO_DB_NAME
        self.mongodb_collection_name = settings.MONGO_COLLECTION_NAME

        # 1. Khởi tạo LLM
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model_name,
            google_api_key=self.google_api_key,
            convert_system_message_to_human=True # Một số model Gemini hoạt động tốt hơn với cách này
        )

        # 2. Khởi tạo Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            google_api_key=self.google_api_key
        )

        # 3. Khởi tạo Pinecone Vector Store và Retriever
        self.vector_store = PineconeVectorStore.from_existing_index(
            index_name=self.pinecone_index_name,
            embedding=self.embeddings,
            # pinecone_api_key=self.pinecone_api_key, # Thường không cần nếu pinecone-client được cấu hình đúng
            # environment=self.pinecone_environment
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3}) # Lấy top 3 kết quả

        # 4. Tạo Retriever Tool
        self.retriever_tool = Tool(
            name="AlgoVaultRetriever",
            func=self.retriever.invoke, # Sử dụng invoke cho retriever đồng bộ
            coroutine=self.retriever.ainvoke, # Sử dụng ainvoke cho retriever bất đồng bộ
            description="Truy xuất thông tin và kiến thức về giải thuật từ cơ sở dữ liệu vector AlgoVault để hỗ trợ việc tạo bài tập.",
        )
        self.tools = [self.retriever_tool]

        # 5. Khởi tạo Output Parser
        self.output_parser = PydanticOutputParser(pydantic_object=ExerciseDetail)
        # self.output_parser = JsonOutputParser(pydantic_object=ExerciseDetail) # JsonOutputParser có thể linh hoạt hơn

        # 6. Tạo Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE.format(format_instructions=self.output_parser.get_format_instructions())),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 7. Tạo Agent
        # Lưu ý: create_tool_calling_agent thường dùng cho các model hỗ trợ "tool calling" rõ ràng.
        # Gemini hỗ trợ điều này, nhưng cú pháp prompt và cách agent hoạt động có thể cần điều chỉnh.
        # Nếu gặp vấn đề, có thể xem xét create_structured_chat_agent hoặc các loại agent khác.
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        # 8. Tạo Agent Executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True, # Đặt thành False trong production
            handle_parsing_errors=True # Xử lý lỗi parsing, có thể trả về thông báo lỗi cho người dùng hoặc thử lại
        )

    def _get_session_history(self, session_id: str) -> MongoDBChatMessageHistory:
        """
        Lấy hoặc tạo lịch sử hội thoại cho một session_id cụ thể từ MongoDB.

        Args:
            session_id (str): ID của session hội thoại.

        Returns:
            MongoDBChatMessageHistory: Đối tượng lịch sử hội thoại.
        """
        return MongoDBChatMessageHistory(
            connection_string=self.mongodb_uri,
            session_id=session_id,
            database_name=self.mongodb_db_name,
            collection_name=self.mongodb_collection_name,
        )

    async def generate_exercise(self, user_query: str, session_id: str) -> ExerciseDetail:
        """
        Tạo một bài tập giải thuật dựa trên yêu cầu của người dùng.

        Args:
            user_query (str): Yêu cầu hoặc chủ đề của bài tập từ người dùng.
            session_id (str): ID của session hội thoại để duy trì ngữ cảnh.

        Returns:
            ExerciseDetail: Đối tượng Pydantic chứa chi tiết bài tập đã được tạo.

        Raises:
            Exception: Nếu có lỗi trong quá trình tạo bài tập hoặc parsing kết quả.
        """
        chat_history_manager = self._get_session_history(session_id)
        
        # Sử dụng RunnableWithMessageHistory để quản lý chat history một cách tự động hơn
        agent_with_chat_history = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id_for_history: self._get_session_history(session_id_for_history),
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="output", # Đảm bảo key này khớp với output của agent_executor
        )

        config = {"configurable": {"session_id": session_id}}
        
        # AgentExecutor trả về một dict, thường có key "output" cho kết quả cuối cùng.
        # Cần kiểm tra cấu trúc output của agent_executor cụ thể này.
        # response = await self.agent_executor.ainvoke({
        #     "input": user_query,
        #     "chat_history": chat_history_manager.messages
        # })
        
        # response_content = response.get("output", "")

        # Khi dùng RunnableWithMessageHistory, response là kết quả cuối cùng (đã xử lý memory)
        # Response từ AgentExecutor với create_tool_calling_agent thường nằm trong 'output'
        response_from_agent = await agent_with_chat_history.ainvoke({"input": user_query}, config=config)
        
        # Response có thể là một Dict nếu agent trả về nhiều thông tin,
        # hoặc string nếu nó trả về output trực tiếp.
        # Với create_tool_calling_agent, key "output" là chuẩn.
        if isinstance(response_from_agent, dict):
            response_content = response_from_agent.get("output")
            if response_content is None:
                # Fallback if 'output' key is missing, try to find a string response.
                # This might happen if the agent structure changes or if an error message is returned differently.
                # It's also possible the entire dict IS the structured response.
                # For now, we assume output parser expects a string.
                # If the LLM is directly outputting JSON for ExerciseDetail, this logic needs adjustment.
                # The current PydanticOutputParser expects a string to parse.
                # If Gemini with tool calling returns a structured dict, then parsing might be direct.
                print(f"Warning: 'output' key not found in agent response. Full response: {response_from_agent}")
                # Heuristic: if it's a dict and looks like our target, try to parse it directly (not with PydanticOutputParser)
                try:
                    # This assumes the agent itself already formed ExerciseDetail compatible dict
                    parsed_exercise = ExerciseDetail.parse_obj(response_from_agent)
                    # No need to update history here as RunnableWithMessageHistory handles it.
                    return parsed_exercise
                except Exception: # Not our target structure
                    response_content = str(response_from_agent) # Fallback to string representation
        elif isinstance(response_from_agent, str):
            response_content = response_from_agent
        else:
            raise ValueError(f"Unexpected response type from agent: {type(response_from_agent)}")


        if not response_content:
            raise Exception("Agent did not produce any output content to parse.")

        try:
            # Phân tích cú pháp output của agent
            parsed_exercise = self.output_parser.parse(response_content)
        except Exception as e:
            # Có thể thêm logic retry hoặc xử lý lỗi parsing ở đây
            # Ví dụ: sử dụng một LLM khác để sửa lỗi JSON
            print(f"Error parsing LLM output: {e}")
            print(f"Raw output was: {response_content}")
            # Fallback: cố gắng parse bằng JsonOutputParser nếu PydanticOutputParser thất bại
            try:
                print("Attempting fallback JSON parsing...")
                json_parser = JsonOutputParser(pydantic_object=ExerciseDetail)
                parsed_exercise = json_parser.parse(response_content)
            except Exception as e2:
                 raise Exception(f"Failed to parse agent output into ExerciseDetail structure. Original error: {e}. Fallback error: {e2}. Raw output: {response_content}") from e2
        
        # RunnableWithMessageHistory đã tự động cập nhật history, không cần gọi add_messages thủ công nữa.
        # chat_history_manager.add_user_message(user_query)
        # chat_history_manager.add_ai_message(response_content) # Lưu trữ raw output

        return parsed_exercise

# Ví dụ sử dụng (chạy khi file được thực thi trực tiếp)
if __name__ == "__main__":
    import asyncio

    async def main():
        # --- Cấu hình ---
        # Đảm bảo các biến môi trường đã được thiết lập trong file .env
        # GOOGLE_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, MONGODB_URI
        
        # Kiểm tra biến môi trường
        required_env_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT", "MONGODB_URI"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            print(f"Lỗi: Vui lòng thiết lập các biến môi trường sau: {', '.join(missing_vars)}")
            print("Ví dụ trong file .env:")
            print("GOOGLE_API_KEY=\"your_google_api_key\"")
            print("PINECONE_API_KEY=\"your_pinecone_api_key\"")
            print("PINECONE_ENVIRONMENT=\"your_pinecone_env\"")
            print("MONGODB_URI=\"mongodb://localhost:27017/\"")
            return

        pinecone_index = "giaithuat" # Thay bằng tên index Pinecone của bạn nếu khác
        
        print("Đang khởi tạo agent...")
        try:
            exercise_agent = GenerateExerciseQuestionAgent(
                pinecone_index_name=pinecone_index,
                # Các tham số khác có thể được cung cấp ở đây nếu không muốn dùng mặc định/env
            )
            print("Agent đã khởi tạo thành công.")
        except ValueError as e:
            print(f"Lỗi khởi tạo agent: {e}")
            return
        except Exception as e:
            print(f"Lỗi không xác định khi khởi tạo agent: {e}")
            # In thêm traceback nếu cần debug
            import traceback
            traceback.print_exc()
            return

        session_id = "my_test_session_123"
        # user_query = "Tạo một bài tập về sắp xếp mảng mức độ dễ, có ngữ cảnh học sinh xếp hàng."
        user_query = "Tạo một bài tập về tìm đường đi ngắn nhất trong đồ thị, mức độ trung bình, với ngữ cảnh người giao hàng."

        print(f"\\nĐang tạo bài tập cho session '{session_id}' với câu hỏi: '{user_query}'")
        
        try:
            generated_exercise = await exercise_agent.generate_exercise(user_query, session_id)
            
            print("\\n--- Bài tập được tạo ---")
            print(f"Tên bài tập: {generated_exercise.name}")
            print(f"Mô tả: {generated_exercise.description}")
            if generated_exercise.constraints:
                print(f"Ràng buộc: {generated_exercise.constraints}")
            if generated_exercise.suggest:
                print(f"Gợi ý: {generated_exercise.suggest}")
            
            print("Các trường hợp thử:")
            for i, test_case in enumerate(generated_exercise.case):
                print(f"  Ví dụ {i+1}:")
                print(f"    Đầu vào: {test_case.input_data}")
                print(f"    Đầu ra: {test_case.output_data}")
                print(f"    Giải thích: {test_case.explain}")
            print("------------------------")

            # Thử hỏi tiếp trong cùng session
            user_query_2 = "Tuyệt vời! Bây giờ hãy cho tôi một bài khác về cấu trúc dữ liệu Hàng đợi (Queue) với độ khó dễ."
            print(f"\\nĐang tạo bài tập tiếp theo cho session '{session_id}' với câu hỏi: '{user_query_2}'")
            generated_exercise_2 = await exercise_agent.generate_exercise(user_query_2, session_id)
            print("\\n--- Bài tập thứ 2 được tạo ---")
            print(f"Tên bài tập: {generated_exercise_2.name}")
            print(f"Mô tả: {generated_exercise_2.description}")
            print("------------------------")

        except Exception as e:
            print(f"Lỗi trong quá trình tạo bài tập: {e}")
            import traceback
            traceback.print_exc()

    # Chạy hàm main
    asyncio.run(main()) 