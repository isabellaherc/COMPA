type BrandMarkProps = {
  className?: string;
};

export function BrandMark({ className = "h-8 w-8" }: BrandMarkProps) {
  return (
    <svg className={className} viewBox="0 0 32 32" aria-hidden="true">
      <ellipse cx="16" cy="7.5" rx="5.4" ry="8" fill="#C1272D" transform="rotate(0 16 16)" />
      <ellipse cx="16" cy="7.5" rx="5.4" ry="8" fill="#FFC5D3" transform="rotate(72 16 16)" />
      <ellipse cx="16" cy="7.5" rx="5.4" ry="8" fill="#C1272D" transform="rotate(144 16 16)" />
      <ellipse cx="16" cy="7.5" rx="5.4" ry="8" fill="#FFC5D3" transform="rotate(216 16 16)" />
      <ellipse cx="16" cy="7.5" rx="5.4" ry="8" fill="#C1272D" transform="rotate(288 16 16)" />
      <circle cx="16" cy="16" r="4" fill="#FF6F91" />
    </svg>
  );
}
