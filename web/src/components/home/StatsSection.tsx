interface Stat {
    value: string;
    label: string;
}

interface StatsSectionProps {
    visible: boolean;
    stats: Stat[];
}

export function StatsSection({ visible, stats }: StatsSectionProps) {
    return (
        <section
            className={`py-20 bg-gradient-to-br from-primary/90 to-secondary/90 text-white transition-all duration-700 ${visible ? "opacity-100" : "opacity-0 translate-y-10"
                }`}
        >
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
    );
} 