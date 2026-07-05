const leaves = Array.from({ length: 16 }, (_, index) => {
  const size = 10 + (index % 4) * 5;
  const sway = (index % 2 === 0 ? 1 : -1) * (24 + (index % 3) * 14);
  return {
    id: index,
    color: ["#FFC5D3", "#FF6F91", "#C1272D"][index % 3],
    size,
    sway,
    left: (index * 61) % 100,
    duration: 16 + (index % 6) * 3,
    delay: -Number(((index * 2.3) % 20).toFixed(1)),
  };
});

export function Canopy() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      {leaves.map((leaf) => (
        <span
          className="leaf-fall absolute -top-10 opacity-0 motion-reduce:animate-none motion-reduce:opacity-30"
          key={leaf.id}
          style={{
            left: `${leaf.left}%`,
            width: leaf.size,
            height: leaf.size * 1.2,
            animationDuration: `${leaf.duration}s`,
            animationDelay: `${leaf.delay}s`,
            "--leaf-sway": `${leaf.sway}px`,
          } as React.CSSProperties}
        >
          <svg viewBox="0 0 20 24" className="block h-full w-full">
            <path d="M10 0C15 6 20 11 10 24C0 11 5 6 10 0Z" fill={leaf.color} />
          </svg>
        </span>
      ))}
    </div>
  );
}
