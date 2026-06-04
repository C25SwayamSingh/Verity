interface Props {
  title: string;
  description: string;
}

export default function CreatorEmptyState({ title, description }: Props) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-giver-mist px-6 py-10 text-center">
      <p className="text-sm font-medium text-giver-ink">{title}</p>
      <p className="mt-2 text-sm text-giver-slate max-w-md mx-auto leading-relaxed">{description}</p>
    </div>
  );
}
