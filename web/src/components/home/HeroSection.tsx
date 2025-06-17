import Link from "next/link";

interface HeroSectionProps {
    visible: boolean;
}

export function HeroSection({ visible }: HeroSectionProps) {
    return (
        <section
            className={`pt-16 pb-24 transition-all duration-700 ${visible ? "opacity-100" : "opacity-0 translate-y-10"
                }`}
        >
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
                                className="px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all"
                            >
                                Khám phá ngay
                            </Link>
                            <Link
                                href="/about"
                                className="px-6 py-3 bg-background border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-all"
                            >
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
    );
} 