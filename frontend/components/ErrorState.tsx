interface ErrorStateProps {
  message: string;
  retryAfterSeconds?: number;
  onRetry?: () => void;
}

export default function ErrorState({
  message,
  retryAfterSeconds,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-6">
      <p className="font-medium text-rose-900">Something went wrong</p>
      <p className="mt-1 text-sm text-rose-800">{message}</p>
      {retryAfterSeconds != null && (
        <p className="mt-2 text-sm text-rose-700">
          Try again in about {retryAfterSeconds} seconds.
        </p>
      )}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md bg-rose-900 px-4 py-2 text-sm text-white hover:bg-rose-800"
        >
          Try again
        </button>
      )}
    </div>
  );
}
