---
applyTo: '**/web/**'
---
# Frontend Instructions
- Khi tạo 1 trang mới (router), thì component page sẽ chỉ tạo component và không có client code, client code sẽ được tạo trong một component khác như sau:
        ```   
            import { LessonPage } from "@/components/pages/learn/LessonPage";
            import { Metadata } from "next";

            interface LessonPageProps {
                params: Promise<{
                    topicId: string;
                    lessonId: string;
                }>;
            }

            // Tạo metadata động dựa trên thông tin bài học
            export async function generateMetadata({ params }: LessonPageProps): Promise<Metadata> {
                const { lessonId } = await params;
                return {
                    title: `Bài học ${lessonId} - AI Agent Giải Thuật`,
                    description: `Học bài học ${lessonId} về giải thuật và lập trình`,
                    authors: [{ name: "AI Agent Giải Thuật Team" }],
                    keywords: ["giải thuật", "học tập", "lập trình", "AI", "bài học"],
                };
            }


            export default async function LessonPageRoute({ params }: LessonPageProps) {
                const { lessonId, topicId } = await params;
                // LessonPage sẽ tự fetch dữ liệu từ API
                return <LessonPage topicId={topicId} lessonId={lessonId} />;
            }
        ```
- Sử dụng các class màu như .text-primary, ..., hãy đọc file `web\src\app\globals.css` để biết các class màu đã được định nghĩa.
- Đang sử dụng pnpm để quản lý package, hãy sử dụng lệnh `pnpm install` để cài đặt package mới.
- Các tên biến, trường của interface, struct tạo ra phải là camelCase.
- Không sử dụng next api routes, đã có fastapi server để xử lý các api.
- Luôn định nghĩa các file api để call http trong thư mục `web\src\lib\api`, ví dụ:
    ```
    web\src\lib\api\learn.ts
    ```