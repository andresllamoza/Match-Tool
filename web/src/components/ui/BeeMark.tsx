export function BeeMark({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3c2.5 0 4.5 1.6 5.2 3.9h2.3a1 1 0 110 2h-1.9c0 .3 0 .7-.1 1h2a1 1 0 110 2h-2.2A5.5 5.5 0 0112 19a5.5 5.5 0 01-5.4-7.1H4.4a1 1 0 110-2h2.1c-.1-.3-.1-.7-.1-1H4.5a1 1 0 110-2h2.3C7.5 4.6 9.5 3 12 3z"
        fill="currentColor"
      />
      <path
        d="M9.5 10.5h5M8 13.5h8"
        stroke="#111111"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
    </svg>
  );
}
