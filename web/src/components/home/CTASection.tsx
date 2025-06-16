import Link from "next/link";

interface CTASectionProps {
    title?: string;
    description?: string;
    buttonText?: string;
    buttonLink?: string;
}

export function CTASection({
    title = "Sẵn sàng bắt đầu?",
    description = "Tham gia ngay hôm nay để nâng cao kỹ năng giải thuật và mở ra cơ hội nghề nghiệp rộng mở",
    buttonText = "Đăng ký miễn phí",
    buttonLink = "/auth/register"
}: CTASectionProps) {
    return (
        <section className="py-20 bg-foreground/5">
            <div className="container mx-auto px-4 text-center">
                <h2 className="text-3xl md:text-4xl font-bold mb-6">{title}</h2>
                <p className="text-lg text-foreground/70 max-w-2xl mx-auto mb-8">
                    {description}
                </p>
                <Link
                    href={buttonLink}
                    className="px-8 py-4 bg-primary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all inline-block"
                >
                    {buttonText}
                </Link>
            </div>
        </section>
    );
} 