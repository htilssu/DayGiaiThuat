import { Metadata } from "next";
import ContactClient from "./ContactClient";

export const metadata: Metadata = {
  title: "Liên hệ hỗ trợ | Ứng dụng học giải thuật thông minh",
  description:
    "Liên hệ với đội ngũ hỗ trợ của chúng tôi để được tư vấn và giải đáp thắc mắc về nền tảng học giải thuật thông minh.",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: [
    "liên hệ",
    "hỗ trợ",
    "tư vấn",
    "giải thuật",
    "học tập",
    "lập trình",
    "AI",
    "customer support",
  ],
};

export default function ContactPage() {
  return <ContactClient />;
}
