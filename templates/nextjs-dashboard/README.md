# VecTrade Next.js Dashboard Template

A Next.js 15 dashboard starter with VecTrade TypeScript SDK integration for building financial data applications.

## Quick Start

```bash
# Clone this template
cp -r templates/nextjs-dashboard my-dashboard
cd my-dashboard

# Install dependencies
pnpm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API key

# Run development server
pnpm dev
```

## Features

- Next.js 15 App Router
- Server-side VecTrade API calls (keeps your API key secret)
- Real-time quote display component
- Portfolio overview page
- Responsive Tailwind CSS layout

## Project Structure

```
my-dashboard/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/
│       └── quote/route.ts
├── components/
│   ├── QuoteCard.tsx
│   └── PortfolioTable.tsx
├── lib/
│   └── vectrade.ts
├── .env.example
├── next.config.ts
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```
