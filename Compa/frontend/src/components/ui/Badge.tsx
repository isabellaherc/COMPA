import type { ReactNode } from "react";

type BadgeVariant = "red" | "pink" | "neutral" | "green";

const variants: Record<BadgeVariant, string> = {
  red: "bg-red/10 text-red",
  pink: "bg-pink text-ink",
  neutral: "bg-surface text-muted",
  green: "bg-green/10 text-green",
};

export function Badge({
  children,
  variant = "neutral",
}: {
  children: ReactNode;
  variant?: BadgeVariant;
}) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${variants[variant]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {children}
    </span>
  );
}
