"use client";

import { useEffect, useState } from "react";
import {
  HeroSection,
  FeaturesSection,
  StatsSection,
  TestimonialsSection,
  CTASection
} from "@/components/home";
import Modal from "@/components/Modal";

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
    <div className="min-h-screen">
      <div>
        <HeroSection visible={heroVisible} />
        <FeaturesSection visible={featuresVisible} features={features} />
        <StatsSection visible={statVisible} stats={stats} />
        <TestimonialsSection />
        <CTASection />
      </div>
    </div>
  );
}
