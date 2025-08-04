import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.evaluation import context_relevancy
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from ragas import EvaluationDataset
from ragas.integrations.llama_index import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision

from env_config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationConfig:
    model_api_key: str
    documents_path: Optional[str] = None
    output_csv_path: str = "rag_evaluation_results.csv"
    model_name: str = "gemini-2.5-flash"

    chunk_size: int = 1024
    chunk_overlap: int = 20

    semantic_breakpoint_percentile_threshold: int = 95
    semantic_buffer_size: int = 1
    # semantic_embedding_model: str = "text-embedding-ada-002"
    semantic_embedding_model: str = "gemini-embedding-004"

    sentence_chunk_size: int = 1024
    sentence_chunk_overlap: int = 200

    token_chunk_size: int = 512
    token_chunk_overlap: int = 50


@dataclass
class EvaluationData:
    """Dữ liệu đánh giá bao gồm câu hỏi và câu trả lời tham chiếu"""

    questions: List[str]
    reference_answers: List[List[str]]

    def __post_init__(self):
        if len(self.questions) != len(self.reference_answers):
            raise ValueError(
                "Số lượng câu hỏi và câu trả lời tham chiếu phải bằng nhau"
            )


def get_all_metrics() -> List:
    """
    Lấy tất cả metrics để đánh giá

    Returns:
        List: Danh sách các metrics
    """
    return [
        faithfulness,
        answer_relevancy,
        context_relevancy,
        context_recall,
        context_precision,
    ]


class RAGEvaluator:
    """Class chính để đánh giá hệ thống RAG"""

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.query_engine: Optional[BaseQueryEngine] = None
        self.embedding_model = GoogleGenAIEmbedding(
            api_key=settings.AI_API_KEY,
            model_name=settings.EMBEDDING_MODEL_NAME)
        self.llm  = GoogleGenAI(api_key=settings.AI_API_KEY)
        self.build_rag_system(config.documents_path)


    def _create_node_parser(self):
        """
        Tạo node parser dựa trên cấu hình chunking strategy

        Returns:
            Node parser phù hợp với strategy được chọn
        """

        return SemanticSplitterNodeParser(
            embed_model=self.embedding_model
        )

    def build_rag_system(self, documents_path: str = None) -> Optional[BaseQueryEngine]:
        """
        Xây dựng hệ thống RAG từ thư mục tài liệu với semantic chunking

        Args:
            documents_path: Đường dẫn tới thư mục chứa tài liệu

        Returns:
            BaseQueryEngine: Engine để thực hiện truy vấn
        """
        try:
            doc_path = documents_path or self.config.documents_path
            if not doc_path:
                raise ValueError("Chưa cung cấp đường dẫn tài liệu")

            logger.info(f"Đang đọc tài liệu từ: {doc_path}")
            documents = SimpleDirectoryReader(input_files=[doc_path]).load_data()
            logger.info(f"Đã đọc {len(documents)} tài liệu")

            node_parser = self._create_node_parser()
            logger.info(f"Sử dụng semantic chunking với mô hình: {self.config.semantic_embedding_model}")

            nodes = node_parser.build_semantic_nodes_from_documents(documents)
            logger.info(f"Đã tạo {len(nodes)} chunks từ tài liệu")

            # Log thông tin về kích thước chunks (để debug)
            if nodes:
                chunk_sizes = [len(node.text) for node in nodes[:5]]  # Lấy 5 chunks đầu
                logger.info(f"Kích thước chunks mẫu: {chunk_sizes}")

            # Tạo VectorStoreIndex từ nodes
            index = VectorStoreIndex(nodes, embed_model=self.embedding_model)

            self.query_engine = index.as_query_engine(llm=self.llm)
            logger.info("Đã xây dựng thành công hệ thống RAG với semantic chunking")

            return self.query_engine

        except Exception as ex:
            logger.error(f"Lỗi khi xây dựng hệ thống RAG: {ex}")
            raise

    def create_sample_evaluation_data(self) -> EvaluationData:
        """
        Tạo dữ liệu đánh giá mẫu - có thể thay thế bằng dữ liệu thực tế

        Returns:
            EvaluationData: Dữ liệu đánh giá mẫu
        """
        sample_questions = [
            "Bạn có thể cung cấp mô tả ngắn gọn về mô hình TinyLlama không?",
            "Tôi muốn biết về các tối ưu hóa tốc độ mà TinyLlama đã thực hiện.",
            "Tại sao TinyLlama sử dụng Grouped-query Attention?",
            "Mô hình TinyLlama có phải là mã nguồn mở không?",
            "Hãy cho tôi biết về tập dữ liệu starcoderdata",
        ]

        sample_answers = [
            [
                "TinyLlama là một mô hình ngôn ngữ nhỏ gọn 1.1B được huấn luyện trên khoảng 1 nghìn tỷ token trong khoảng 3 epoch. Dựa trên kiến trúc và tokenizer của Llama 2, TinyLlama tận dụng các tiến bộ từ cộng đồng mã nguồn mở như FlashAttention, đạt được hiệu quả tính toán tốt hơn."
            ],
            [
                "Trong quá trình huấn luyện, codebase đã tích hợp FSDP để tận dụng hiệu quả thiết lập multi-GPU và multi-node. Một cải tiến quan trọng khác là tích hợp Flash Attention, một cơ chế attention được tối ưu hóa."
            ],
            [
                "Để giảm overhead băng thông bộ nhớ và tăng tốc độ suy luận, chúng tôi sử dụng grouped-query attention trong mô hình. Chúng tôi có 32 head cho query attention và sử dụng 4 nhóm key-value head."
            ],
            ["Có, TinyLlama là mã nguồn mở"],
            [
                "Tập dữ liệu này được thu thập để huấn luyện StarCoder, một mô hình ngôn ngữ lớp lớn mã nguồn mở mạnh mẽ. Nó bao gồm khoảng 250 tỷ token trên 86 ngôn ngữ lập trình."
            ],
        ]

        return EvaluationData(
            questions=sample_questions, reference_answers=sample_answers
        )

    def evaluate_rag_system(
            self, evaluation_data: EvaluationData, metrics: Optional[List] = None
    ) -> pd.DataFrame:
        """
        Đánh giá hệ thống RAG với dữ liệu và metrics được cung cấp

        Args:
            evaluation_data: Dữ liệu đánh giá
            metrics: Danh sách metrics (nếu None sẽ sử dụng tất cả)

        Returns:
            pd.DataFrame: Kết quả đánh giá
        """

        if not self.query_engine:
            raise ValueError(
                "Chưa xây dựng hệ thống RAG. Gọi build_rag_system() trước."
            )

        if metrics is None:
            metrics = get_all_metrics()

        logger.info(f"Bắt đầu đánh giá với {len(evaluation_data.questions)} câu hỏi")
        logger.info(f"Sử dụng {len(metrics)} metrics")

        try:


            dataset = EvaluationDataset(evaluation_data)




            # Thực hiện đánh giá
            result = evaluate(
                query_engine=self.query_engine,
                dataset=dataset,
                metrics=metrics,
            )

            # Chuyển đổi kết quả thành DataFrame
            df_result = result.to_pandas()

            # Thêm timestamp
            df_result["evaluation_timestamp"] = datetime.now()

            logger.info("Đánh giá hoàn thành thành công")
            return df_result

        except Exception as e:
            logger.error(f"Lỗi trong quá trình đánh giá: {e}")
            raise

    def save_results(self, results: pd.DataFrame, output_path: Optional[str] = None):
        """
        Lưu kết quả đánh giá ra file CSV

        Args:
            results: DataFrame chứa kết quả
            output_path: Đường dẫn file output (nếu None sẽ dùng config)
        """
        output_file = output_path or self.config.output_csv_path

        try:
            results.to_csv(output_file, sep=",", index=False, encoding="utf-8")
            logger.info(f"Đã lưu kết quả đánh giá vào: {output_file}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu file: {e}")
            raise

    def generate_evaluation_report(self, results: pd.DataFrame) -> Dict[str, Any]:
        """
        Tạo báo cáo tóm tắt kết quả đánh giá

        Args:
            results: DataFrame chứa kết quả đánh giá

        Returns:
            Dict: Báo cáo tóm tắt
        """
        numeric_columns = results.select_dtypes(include=["float64", "int64"]).columns

        report = {
            "overview": {
                "total_questions": len(results),
                "evaluation_date": datetime.now().isoformat(),
                "metrics_evaluated": list(numeric_columns),
            },
            "summary_statistics": {
                col: {
                    "mean": float(results[col].mean()),
                    "std": float(results[col].std()),
                    "min": float(results[col].min()),
                    "max": float(results[col].max()),
                    "median": float(results[col].median()),
                }
                for col in numeric_columns
            },
            "performance_insights": self._analyze_performance(
                results, list(numeric_columns)
            ),
        }

        return report

    def _analyze_performance(
            self, results: pd.DataFrame, metric_columns: List[str]
    ) -> Dict[str, str]:
        """
        Phân tích hiệu suất dựa trên kết quả

        Args:
            results: DataFrame chứa kết quả
            metric_columns: Danh sách tên cột metrics

        Returns:
            Dict: Phân tích hiệu suất
        """
        insights = {}

        for col in metric_columns:
            mean_score = results[col].mean()
            if mean_score >= 0.8:
                insights[col] = "Excellent performance"
            elif mean_score >= 0.6:
                insights[col] = "Good performance"
            elif mean_score >= 0.4:
                insights[col] = "Average performance - needs improvement"
            else:
                insights[col] = "Poor performance - requires significant improvement"

        return insights


def run_sample_evaluation():
    """
    Chạy đánh giá mẫu với dữ liệu demo

    Đây là hàm demo để kiểm tra hoạt động của framework
    """
    # Cấu hình đánh giá
    config = EvaluationConfig(
        model_api_key=settings.AI_API_KEY,
        documents_path="document.pdf",
        output_csv_path="sample_rag_evaluation.csv",
        semantic_embedding_model=settings.EMBEDDING_MODEL_NAME,
    )

    try:
        evaluator = RAGEvaluator(config)

        eval_data = evaluator.create_sample_evaluation_data()
        evaluation_result = evaluator.evaluate_rag_system(eval_data)
        evaluator.save_results(evaluation_result)

        # Hiển thị câu hỏi mẫu
        print("\n📋 Câu hỏi mẫu:")
        for i, question in enumerate(eval_data.questions[:3], 1):
            print(f"   {i}. {question}")
        print("   ...")

    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    print("🚀 RAG Evaluation Framework")
    print("=" * 50)
    run_sample_evaluation()
