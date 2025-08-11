"use client";

import { useState } from "react";
import {
  IconMail,
  IconPhone,
  IconMapPin,
  IconClock,
  IconBrandFacebook,
  IconBrandGithub,
  IconBrandTwitter,
  IconSend,
  IconCheck,
} from "@tabler/icons-react";

interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

const contactInfo = [
  {
    icon: IconMail,
    title: "Email",
    value: "inuka072025@gmail.com",
    description: "Gửi email trực tiếp cho chúng tôi",
    link: "mailto:inuka072025@gmail.com",
  },
  {
    icon: IconPhone,
    title: "Điện thoại",
    value: "+84 935 271 776",
    description: "Gọi điện thoại trong giờ hành chính",
    link: "tel:+84935271776",
  },
  {
    icon: IconMapPin,
    title: "Địa chỉ",
    value: "Hồ Chí Minh, Việt Nam",
    description: "Trụ sở chính của chúng tôi",
    link: "#",
  },
  {
    icon: IconClock,
    title: "Giờ làm việc",
    value: "8:00 - 18:00 (GMT+7)",
    description: "Thứ 2 - Thứ 6 hàng tuần",
    link: "#",
  },
];

const socialLinks = [
  {
    icon: IconBrandFacebook,
    name: "Facebook",
    url: "https://facebook.com/aigiaithuat",
    color: "hover:text-blue-600",
  },
  {
    icon: IconBrandGithub,
    name: "GitHub",
    url: "https://github.com/aigiaithuat",
    color: "hover:text-gray-800 dark:hover:text-gray-200",
  },
  {
    icon: IconBrandTwitter,
    name: "Twitter",
    url: "https://twitter.com/aigiaithuat",
    color: "hover:text-blue-400",
  },
];

export default function ContactClient() {
  const [formData, setFormData] = useState<ContactForm>({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 2000));

    setIsSubmitting(false);
    setIsSubmitted(true);

    // Reset form after 3 seconds
    setTimeout(() => {
      setIsSubmitted(false);
      setFormData({
        name: "",
        email: "",
        subject: "",
        message: "",
      });
    }, 3000);
  };

  return (
    <div className="min-h-screen py-16 bg-gradient-to-br from-primary/5 via-background to-background">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="py-2 text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-primary">
            Liên hệ với chúng tôi
          </h1>
          <p className="text-lg text-foreground/80 max-w-2xl mx-auto">
            Bạn có câu hỏi, góp ý hoặc cần hỗ trợ? Chúng tôi luôn sẵn sàng lắng
            nghe và hỗ trợ bạn!
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 mb-16">
          {/* Contact Form */}
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-4">
                Gửi tin nhắn cho chúng tôi
              </h2>
              <p className="text-foreground/70 mb-6">
                Điền form bên dưới và chúng tôi sẽ phản hồi trong thời gian sớm
                nhất.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-foreground mb-2">
                    Họ và tên *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg border border-foreground/20 bg-background text-foreground placeholder-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
                    placeholder="Nhập họ và tên của bạn"
                  />
                </div>
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-foreground mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg border border-foreground/20 bg-background text-foreground placeholder-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
                    placeholder="Nhập email của bạn"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="subject"
                  className="block text-sm font-medium text-foreground mb-2">
                  Tiêu đề *
                </label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 rounded-lg border border-foreground/20 bg-background text-foreground placeholder-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
                  placeholder="Nhập chủ đề tin nhắn"
                />
              </div>

              <div>
                <label
                  htmlFor="message"
                  className="block text-sm font-medium text-foreground mb-2">
                  Nội dung tin nhắn *
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  rows={6}
                  className="w-full px-4 py-3 rounded-lg border border-foreground/20 bg-background text-foreground placeholder-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200 resize-none"
                  placeholder="Nhập nội dung tin nhắn của bạn..."
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-primary to-secondary text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Đang gửi...
                  </>
                ) : isSubmitted ? (
                  <>
                    <IconCheck className="w-5 h-5" />
                    Đã gửi thành công!
                  </>
                ) : (
                  <>
                    <IconSend className="w-5 h-5" />
                    Gửi tin nhắn
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Contact Information */}
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-4">
                Thông tin liên hệ
              </h2>
              <p className="text-foreground/70 mb-6">
                Liên hệ với chúng tôi qua các kênh sau đây.
              </p>
            </div>

            <div className="space-y-6">
              {contactInfo.map((info, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 rounded-lg bg-background border border-foreground/10 hover:shadow-md transition-all duration-200">
                  <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                    <info.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">
                      {info.title}
                    </h3>
                    <a
                      href={info.link}
                      className="text-primary hover:text-secondary transition-colors duration-200 font-medium">
                      {info.value}
                    </a>
                    <p className="text-sm text-foreground/70 mt-1">
                      {info.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Social Links */}
            <div>
              <h3 className="font-semibold text-foreground mb-4">
                Theo dõi chúng tôi
              </h3>
              <div className="flex space-x-4">
                {socialLinks.map((social, index) => (
                  <a
                    key={index}
                    href={social.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`w-12 h-12 bg-background border border-foreground/20 rounded-lg flex items-center justify-center text-foreground/70 transition-all duration-200 hover:shadow-md ${social.color}`}>
                    <social.icon className="w-6 h-6" />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
