interface NeutralRewriteProps {
  text: string;
  eligible: boolean;
}

export default function NeutralRewrite({ text, eligible }: NeutralRewriteProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold text-giver-ink">Neutral rewrite</h2>
      {!eligible && (
        <p className="mt-1 text-xs text-giver-slate">
          Not generated for ineligible content categories.
        </p>
      )}
      <p className="mt-3 text-sm leading-relaxed text-giver-ink">{text}</p>
    </section>
  );
}
