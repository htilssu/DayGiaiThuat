import { keyframes } from "@emotion/react";

const bounce = keyframes`
  0%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-6px);
  }
`;

export default function LoadingDots() {
  return (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((index) => (
        <div
          key={index}
          className="w-2 h-2 bg-[rgb(var(--color-primary))] rounded-full"
          style={{
            animation: `${bounce} 1s infinite`,
            animationDelay: `${index * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}
