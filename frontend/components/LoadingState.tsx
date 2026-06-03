export default function LoadingState() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
      <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-giver-accent border-t-transparent" />
      <p className="font-medium text-giver-ink">Analyzing content…</p>
      <p className="mt-1 text-sm text-giver-slate">
        Extracting claims, checking source alignment, and reviewing framing signals.
      </p>
    </div>
  );
}
