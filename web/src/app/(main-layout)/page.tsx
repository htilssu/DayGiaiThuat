"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

/**
 * Trang chủ của ứng dụng
 * Hiển thị thông tin chính và điều hướng đến các tính năng chính
 *
 * @returns {JSX.Element} Trang chủ
 */
export default function HomePage() {
  // Trạng thái hiển thị các phần tử theo hiệu ứng
  const [heroVisible, setHeroVisible] = useState(false);
  const [featuresVisible, setFeaturesVisible] = useState(false);
  const [statVisible, setStatVisible] = useState(false);

  // Các tính năng chính của ứng dụng
  const features = [
    {
      title: "Thư viện giải thuật",
      description:
        "Tìm hiểu và thực hành với hơn 500+ giải thuật phổ biến được phân loại theo độ khó",
      icon: (
        <svg
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
      ),
    },
    {
      title: "AI Assistant",
      description:
        "Trợ lý AI thông minh hỗ trợ giải đáp và hướng dẫn từng bước giải quyết bài toán",
      icon: (
        <svg
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      ),
    },
    {
      title: "Thực hành trực tuyến",
      description:
        "Thử thách bản thân với các bài tập từ cơ bản đến nâng cao, có đánh giá tự động",
      icon: (
        <svg
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      title: "Cộng đồng học tập",
      description:
        "Kết nối với cộng đồng hơn 10,000 lập trình viên, chia sẻ kinh nghiệm và giải pháp",
      icon: (
        <svg
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      ),
    },
  ];

  // Các thống kê về ứng dụng
  const stats = [
    { value: "20,000+", label: "Người học" },
    { value: "500+", label: "Giải thuật" },
    { value: "10,000+", label: "Bài tập" },
    { value: "98%", label: "Hài lòng" },
  ];

  // Hiệu ứng hiển thị các phần tử
  useEffect(() => {
    // Hiệu ứng hiển thị các phần tử
    setTimeout(() => setHeroVisible(true), 300);
    setTimeout(() => setFeaturesVisible(true), 600);
    setTimeout(() => setStatVisible(true), 900);
  }, []);

  return (
    <div className="relative min-h-screen">
      {/* Nội dung trang */}
      <div className="relative z-10">
        {/* Phần Hero */}
        <section
          className={`pt-16 pb-24 transition-all duration-700 ${
            heroVisible ? "opacity-100" : "opacity-0 translate-y-10"
          }`}>
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center">
              <div className="md:w-1/2 mb-12 md:mb-0 md:pr-8">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gradient-theme py-5">
                  Học thuật toán hiệu quả cùng AI
                </h1>
                <p className="text-lg md:text-xl mb-8 text-foreground/80 max-w-xl">
                  Nền tảng học thuật toán thông minh giúp bạn nắm vững các giải
                  thuật cơ bản và nâng cao thông qua thực hành tương tác và trợ
                  lý AI cá nhân hóa.
                </p>
                <div className="flex flex-wrap gap-4">
                  <Link
                    href="/algorithms"
                    className="px-6 py-3 btn-gradient-primary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all">
                    Khám phá ngay
                  </Link>
                  <Link
                    href="/about"
                    className="px-6 py-3 bg-background border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-all">
                    Tìm hiểu thêm
                  </Link>
                </div>
              </div>
              <div className="md:w-1/2 flex justify-center">
                <div className="relative w-full max-w-lg aspect-square">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-3xl transform rotate-6"></div>
                  <div className="absolute inset-0 bg-background rounded-3xl shadow-xl transform -rotate-3 overflow-hidden border border-foreground/10">
                    <div className="p-8 h-full flex flex-col">
                      <div className="flex items-center space-x-2 mb-4">
                        <div className="w-3 h-3 rounded-full bg-accent"></div>
                        <div className="w-3 h-3 rounded-full bg-secondary"></div>
                        <div className="w-3 h-3 rounded-full bg-primary"></div>
                      </div>
                      <div className="flex-grow flex flex-col p-4 space-y-4">
                        <div className="bg-foreground/5 rounded-lg p-4">
                          <pre className="text-xs text-foreground/80">
                            <code>{`function quickSort(arr) {
                            if (arr.length <= 1) {
                              return arr;
                            }
                            
                            const pivot = arr[0];
                            const left = [];
                            const right = [];
                            
                            for (let i = 1; i < arr.length; i++) {
                              if (arr[i] < pivot) {
                                left.push(arr[i]);
                              } else {
                                right.push(arr[i]);
                              }
                            }
                            
                            return [...quickSort(left), pivot, ...quickSort(right)];
                          }`}</code>
                          </pre>
                        </div>
                        <div className="bg-primary/10 rounded-lg p-4">
                          <p className="text-sm text-foreground/80">
                            <span className="text-primary font-bold">
                              AI Assistant:
                            </span>{" "}
                            Thuật toán QuickSort hoạt động theo nguyên tắc chia
                            để trị, có độ phức tạp trung bình là O(n log n)...
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Phần tính năng */}
        <section
          className={`py-20 bg-foreground/5 rounded-t-[3rem] transition-all duration-700 ${
            featuresVisible ? "opacity-100" : "opacity-0 translate-y-10"
          }`}>
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Tính năng nổi bật
              </h2>
              <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
                Trải nghiệm học tập hiệu quả với các công cụ thông minh và tài
                nguyên chất lượng cao
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-background rounded-xl p-6 shadow-lg border border-foreground/10 hover:shadow-xl transition-all hover:border-primary/20">
                  <div className="p-3 mb-4 rounded-lg bg-primary/10 w-max text-primary">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-foreground/70">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Phần thống kê */}
        <section
          className={`py-20 bg-gradient-to-br from-primary/90 to-secondary/90 text-white transition-all duration-700 ${
            statVisible ? "opacity-100" : "opacity-0 translate-y-10"
          }`}>
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-4xl md:text-5xl font-bold mb-2">
                    {stat.value}
                  </div>
                  <div className="text-white/80">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Phần Lời chứng thực */}
        <section className="py-20 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Người học nói gì?
              </h2>
              <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
                Khám phá trải nghiệm học tập của cộng đồng
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[1, 2, 3].map((_, index) => (
                <div
                  key={index}
                  className="bg-foreground/5 rounded-xl p-6 border border-foreground/10">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mr-4">
                      <span className="text-xl font-bold text-primary">
                        {String.fromCharCode(65 + index)}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-semibold">Học viên {index + 1}</h4>
                      <p className="text-sm text-foreground/60">
                        Sinh viên CNTT
                      </p>
                    </div>
                  </div>
                  <p className="text-foreground/80">
                    &ldquo;Nền tảng giúp tôi hiểu rõ các thuật toán phức tạp một
                    cách dễ dàng. Trợ lý AI thực sự hữu ích khi giải thích từng
                    bước của thuật toán.&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Phần CTA */}
        <section className="py-20 bg-foreground/5">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Sẵn sàng bắt đầu?
            </h2>
            <p className="text-lg text-foreground/70 max-w-2xl mx-auto mb-8">
              Tham gia ngay hôm nay để nâng cao kỹ năng giải thuật và mở ra cơ
              hội nghề nghiệp rộng mở
            </p>
            <Link
              href="/auth/register"
              className="px-8 py-4 btn-gradient-primary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all inline-block">
              Đăng ký miễn phí
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
