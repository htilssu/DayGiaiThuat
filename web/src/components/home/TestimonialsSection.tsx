interface Testimonial {
    name: string;
    role: string;
    content: string;
}

interface TestimonialsSectionProps {
    testimonials?: Testimonial[];
}

export function TestimonialsSection({ testimonials }: TestimonialsSectionProps) {
    // Nếu không có dữ liệu, sử dụng dữ liệu mẫu
    const defaultTestimonials = [
        {
            name: "Học viên 1",
            role: "Sinh viên CNTT",
            content: "Nền tảng giúp tôi hiểu rõ các thuật toán phức tạp một cách dễ dàng. Trợ lý AI thực sự hữu ích khi giải thích từng bước của thuật toán."
        },
        {
            name: "Học viên 2",
            role: "Sinh viên CNTT",
            content: "Nền tảng giúp tôi hiểu rõ các thuật toán phức tạp một cách dễ dàng. Trợ lý AI thực sự hữu ích khi giải thích từng bước của thuật toán."
        },
        {
            name: "Học viên 3",
            role: "Sinh viên CNTT",
            content: "Nền tảng giúp tôi hiểu rõ các thuật toán phức tạp một cách dễ dàng. Trợ lý AI thực sự hữu ích khi giải thích từng bước của thuật toán."
        }
    ];

    const displayTestimonials = testimonials || defaultTestimonials;

    return (
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
                    {displayTestimonials.map((testimonial, index) => (
                        <div
                            key={index}
                            className="bg-foreground/5 rounded-xl p-6 border border-foreground/10"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mr-4">
                                    <span className="text-xl font-bold text-primary">
                                        {String.fromCharCode(65 + index)}
                                    </span>
                                </div>
                                <div>
                                    <h4 className="font-semibold">{testimonial.name}</h4>
                                    <p className="text-sm text-foreground/60">{testimonial.role}</p>
                                </div>
                            </div>
                            <p className="text-foreground/80">&ldquo;{testimonial.content}&rdquo;</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
} 