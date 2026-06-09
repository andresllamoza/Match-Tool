"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { EmbedWidget } from "./EmbedWidget";

function EmbedContent() {
  const searchParams = useSearchParams();
  const initialEmployer = searchParams.get("employer") ?? "";

  return <EmbedWidget initialEmployer={initialEmployer} />;
}

export function EmbedPageClient() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[32rem] items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
        </div>
      }
    >
      <EmbedContent />
    </Suspense>
  );
}
