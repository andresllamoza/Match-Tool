import { ReactNode } from "react";

export function ChannelSection({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`space-y-6 ${className}`}>{children}</section>;
}
