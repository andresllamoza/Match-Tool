import { EmbedWidget } from "@/components/EmbedWidget";

export default function EmbedPage() {
  return (
    <main className="mx-auto max-w-journey px-4 py-8 lg:max-w-2xl lg:py-12">
      <div className="mb-6 rounded-card border border-bee-border bg-white p-5 lg:p-6">
        <h1 className="text-lg font-bold text-bee-blue lg:text-xl">Embed mode</h1>
        <p className="mt-2 text-sm text-bee-muted lg:text-base">
          Drop this into PensionBee&apos;s &quot;Add a transfer&quot; step via iframe or React mount.
        </p>
        <pre className="mt-4 overflow-x-auto rounded-card bg-cream-dark p-4 text-xs lg:text-sm">
{`<iframe
  src="https://your-host/embed"
  title="Rollover Companion"
  style="width:100%;min-height:640px;border:none;border-radius:16px"
/>`}
        </pre>
      </div>
      <EmbedWidget />
    </main>
  );
}
