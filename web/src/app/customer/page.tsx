import { redirect } from "next/navigation";

type CustomerPageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

function toQueryString(params: Record<string, string | string[] | undefined>): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === "string") {
      qs.set(key, value);
    } else if (Array.isArray(value)) {
      for (const item of value) {
        qs.append(key, item);
      }
    }
  }
  return qs.toString();
}

/** Discovery Streamlit hands off to /customer?employer=… — forward params to /app. */
export default function CustomerPage({ searchParams = {} }: CustomerPageProps) {
  const query = toQueryString(searchParams);
  redirect(query ? `/app?${query}` : "/app");
}
