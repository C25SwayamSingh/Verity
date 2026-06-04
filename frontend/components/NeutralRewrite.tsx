interface NeutralRewriteProps {
  text: string;
  eligible: boolean;
}

export default function NeutralRewrite({ text, eligible }: NeutralRewriteProps) {
  if (!text) return null;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold text-giver-ink">
        {eligible ? "Neutral rewrite" : "Clearer rewrite"}
      </h2>
      {!eligible && (
        <p className="mt-1 text-xs text-giver-slate">
          Full news bias/framing analysis isn&apos;t available for this category, but here is a
          clearer rewrite of the submitted text.
        </p>
      )}
      <p className="mt-3 text-sm leading-relaxed text-giver-ink">{text}</p>
    </section>
  );
}
