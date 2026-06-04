import Link from "next/link";

interface Props {
  title: string;
  description: string;
  actionHref?: string;
  actionLabel?: string;
}

export default function CreatorEmptyState({
  title,
  description,
  actionHref,
  actionLabel,
}: Props) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-giver-mist px-6 py-10 text-center">
      <p className="text-sm font-medium text-giver-ink">{title}</p>
      <p className="mt-2 text-sm text-giver-slate max-w-md mx-auto leading-relaxed">{description}</p>
      {actionHref && actionLabel && (
        <Link
          href={actionHref}
          className="mt-4 inline-flex items-center rounded-md bg-giver-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
