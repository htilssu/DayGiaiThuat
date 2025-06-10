"use client";

import { motion } from "framer-motion";
import { IconBrain, IconCode, IconUsers, IconRobot } from "@tabler/icons-react";

export default function AboutPage() {
  const features = [
    {
      icon: <IconBrain className="w-6 h-6" />,
      title: "Thư viện giải thuật",
      description:
        "Kho tàng với hơn 500+ giải thuật được phân loại và giải thích chi tiết, từ cơ bản đến nâng cao.",
    },
    {
      icon: <IconRobot className="w-6 h-6" />,
      title: "AI Assistant",
      description:
        "Trợ lý thông minh 24/7 hỗ trợ giải đáp thắc mắc và hướng dẫn giải quyết bài toán theo từng bước.",
    },
    {
      icon: <IconCode className="w-6 h-6" />,
      title: "Thực hành trực tuyến",
      description:
        "Môi trường thực hành trực tuyến với hệ thống chấm bài tự động và phản hồi chi tiết.",
    },
    {
      icon: <IconUsers className="w-6 h-6" />,
      title: "Cộng đồng học tập",
      description:
        "Kết nối với cộng đồng hơn 10,000 lập trình viên, chia sẻ kinh nghiệm và học hỏi lẫn nhau.",
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section with Diagonal Design */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary/10 via-background to-background">
        <div className="absolute inset-0 bg-grid-white opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-primary">
              AI Agent Giải Thuật
            </h1>
            <p className="text-xl md:text-2xl text-foreground/80 max-w-3xl mx-auto leading-relaxed">
              Nơi công nghệ AI và giáo dục gặp nhau, tạo nên trải nghiệm học
              thuật toán độc đáo và hiệu quả cho thế hệ lập trình viên tương
              lai.
            </p>
          </motion.div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-background to-transparent"></div>
      </div>

      {/* Vision Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
        className="py-20 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4">
          <div className="relative z-10 grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Tầm nhìn của chúng tôi
              </h2>
              <p className="text-lg text-foreground/80 leading-relaxed">
                Chúng tôi tin rằng mỗi người đều có tiềm năng trở thành một lập
                trình viên xuất sắc. Với sự kết hợp giữa công nghệ AI tiên tiến
                và phương pháp giảng dạy được cá nhân hóa, chúng tôi đang định
                hình lại cách mọi người học và áp dụng các giải thuật trong thực
                tế.
              </p>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-3xl transform rotate-3"></div>
              <div className="relative bg-foreground/5 rounded-3xl p-8 transform -rotate-3 border border-foreground/10">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                      <IconBrain className="w-6 h-6 text-primary" />
                    </div>
                    <div className="text-xl font-semibold">
                      20,000+ Người học
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                      <IconCode className="w-6 h-6 text-secondary" />
                    </div>
                    <div className="text-xl font-semibold">500+ Giải thuật</div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center">
                      <IconUsers className="w-6 h-6 text-accent" />
                    </div>
                    <div className="text-xl font-semibold">98% Hài lòng</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Features Section with Interactive Cards */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
        className="py-20 bg-foreground/5">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Tính năng nổi bật
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.02 }}
                className="group relative bg-background rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary/20 transition-colors duration-300">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-foreground/70 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Team Section with Modern Design */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true }}
        className="py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="relative inline-block">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Đội ngũ phát triển
            </h2>
            <div className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-primary via-secondary to-primary rounded-full"></div>
          </div>
          <p className="text-lg text-foreground/80 max-w-3xl mx-auto mt-8 leading-relaxed">
            Chúng tôi là những chuyên gia đam mê công nghệ và giáo dục, với sứ
            mệnh giúp đỡ thế hệ lập trình viên tương lai phát triển kỹ năng và
            đạt được ước mơ của họ thông qua nền tảng học tập thông minh và hiệu
            quả.
          </p>
        </div>
      </motion.section>
    </div>
  );
}
