import { ReactNode } from "react";

interface Feature {
    title: string;
    description: string;
    icon: ReactNode;
}

interface FeaturesSectionProps {
    visible: boolean;
    features: Feature[];
}

export function FeaturesSection({ visible, features }: FeaturesSectionProps) {
    return (
        <section
            className={`py-20 bg-foreground/5 rounded-t-[3rem] transition-all duration-700 ${visible ? "opacity-100" : "opacity-0 translate-y-10"
                }`}
        >
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
                            className="bg-background rounded-xl p-6 shadow-lg border border-foreground/10 hover:shadow-xl transition-all hover:border-primary/20"
                        >
                            <div className="p-3 mb-4 rounded-lg bg-primary/10 w-max text-primary">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                            <p className="text-foreground/70">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
} 