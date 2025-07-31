"use client";

// import { Metadata } from "next";
import { useState } from "react";
import { IconChevronDown, IconChevronRight } from "@tabler/icons-react";

// export const metadata: Metadata = {
//   title: "Câu hỏi thường gặp (FAQ) | Ứng dụng học giải thuật thông minh",
//   description:
//     "Giải đáp các thắc mắc thường gặp về cách sử dụng nền tảng học giải thuật thông minh với AI Assistant.",
//   authors: [{ name: "AI Agent Giải Thuật Team" }],
//   keywords: [
//     "giải thuật",
//     "học tập",
//     "lập trình",
//     "AI",
//     "bài tập",
//     "FAQ",
//     "hướng dẫn sử dụng",
//   ],
// };

const faqs = [
  {
    question: "Ứng dụng này dùng để làm gì?",
    answer:
      "Đây là nền tảng học giải thuật thông minh, giúp bạn học, luyện tập và kiểm tra kiến thức về giải thuật với sự hỗ trợ của AI Assistant. Bạn có thể học lý thuyết, thực hành, hỏi đáp và tham gia cộng đồng lập trình viên.",
  },
  {
    question: "Làm sao để bắt đầu học một giải thuật?",
    answer:
      'Bạn hãy vào mục "Khóa học" hoặc "Chủ đề", chọn giải thuật hoặc chủ đề bạn muốn học. Mỗi bài học đều có lý thuyết, ví dụ minh họa, bài tập thực hành và phần kiểm tra kiến thức.',
  },
  {
    question: "AI Assistant hỗ trợ gì cho tôi?",
    answer:
      "AI Assistant có thể giải đáp thắc mắc, hướng dẫn giải bài tập từng bước, gợi ý cách tiếp cận bài toán, giải thích lý thuyết và giúp bạn luyện tập hiệu quả hơn.",
  },
  {
    question: "Tôi có thể luyện tập và kiểm tra kiến thức như thế nào?",
    answer:
      "Bạn có thể làm bài tập thực hành trực tuyến, hệ thống sẽ tự động chấm điểm và phản hồi chi tiết. Ngoài ra, bạn có thể tham gia các bài kiểm tra tổng hợp để đánh giá trình độ của mình.",
  },
  {
    question: "Làm sao để hỏi đáp hoặc thảo luận với cộng đồng?",
    answer:
      'Bạn hãy vào mục "Thảo luận" để đặt câu hỏi, trả lời hoặc trao đổi kinh nghiệm với các thành viên khác. Đây là nơi bạn có thể học hỏi và chia sẻ kiến thức cùng cộng đồng.',
  },
  {
    question: "Tôi có thể lưu tiến trình học tập không?",
    answer:
      'Có. Ứng dụng sẽ tự động lưu tiến trình học, các khóa học đã tham gia, bài tập đã làm và kết quả kiểm tra của bạn. Bạn có thể xem lại bất cứ lúc nào trong phần "Hồ sơ cá nhân".',
  },
  {
    question: "Làm sao để đăng nhập hoặc đăng ký tài khoản?",
    answer:
      'Bạn nhấn vào nút "Đăng nhập" hoặc "Đăng ký" ở góc trên bên phải màn hình, sau đó làm theo hướng dẫn. Việc đăng ký tài khoản giúp bạn lưu trữ tiến trình học và tham gia cộng đồng dễ dàng hơn.',
  },
  {
    question: "Tôi gặp lỗi hoặc có góp ý, phải làm sao?",
    answer:
      'Bạn có thể gửi phản hồi qua mục "Liên hệ hỗ trợ" hoặc gửi email cho đội ngũ phát triển. Chúng tôi luôn lắng nghe và sẵn sàng hỗ trợ bạn!',
  },
];

export default function FAQPage() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen py-16 bg-gradient-to-br from-primary/5 via-background to-background">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-primary">
          Câu hỏi thường gặp (FAQ)
        </h1>
        <p className="text-lg text-foreground/80 text-center mb-12">
          Dưới đây là những thắc mắc phổ biến về cách sử dụng nền tảng học giải
          thuật thông minh. Nếu bạn còn câu hỏi khác, hãy liên hệ với chúng tôi!
        </p>
        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-background shadow-md border border-foreground/10 hover:shadow-lg transition-all duration-300 overflow-hidden">
              <button
                onClick={() => toggleFAQ(idx)}
                className="w-full p-6 text-left flex items-center justify-between hover:bg-foreground/5 transition-colors duration-200">
                <h2 className="text-xl font-semibold text-primary pr-4">
                  {faq.question}
                </h2>
                {expandedIndex === idx ? (
                  <IconChevronDown className="w-6 h-6 text-primary flex-shrink-0" />
                ) : (
                  <IconChevronRight className="w-6 h-6 text-primary flex-shrink-0" />
                )}
              </button>
              {expandedIndex === idx && (
                <div className="px-6 pb-6 animate-in slide-in-from-top-2 duration-200">
                  <p className="text-foreground/80 leading-relaxed border-t border-foreground/10 pt-4">
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
