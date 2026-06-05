# Verity — Frontend

Next.js App Router UI for the Phase 1 Core Checker MVP.

## Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to your backend (default `http://localhost:8000`).

## Pages

- `/` — paste text, select category, analyze
- `/results/[id]` — view stored analysis

## Stack

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
