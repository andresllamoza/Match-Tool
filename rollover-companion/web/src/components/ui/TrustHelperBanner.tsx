export function TrustHelperBanner({
  children,
  variant = "warm",
}: {
  children: React.ReactNode;
  variant?: "warm" | "neutral";
}) {
  const styles =
    variant === "warm"
      ? "border-[#EAE5DC] bg-[#FFF9E6] text-[#1E242B]"
      : "border-[#EAE5DC] bg-[#FAF8F5] text-[#1E242B]";

  return (
    <div
      className={`rounded-xl border px-5 py-4 text-sm leading-relaxed lg:text-base ${styles}`}
      role="status"
    >
      {children}
    </div>
  );
}
