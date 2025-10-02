# Frontend Interview Project

A modern React starter template built with Next.js 15, TypeScript, and Tailwind CSS for frontend coding interviews.

## Tech Stack

- **Next.js 15.5** with App Router
- **React 19** with Server Components
- **TypeScript 5**
- **Tailwind CSS 4**
- **Turbopack** for fast development and builds
- **ESLint** for code quality

## Getting Started

### Prerequisites

- Node.js 20+ installed
- npm or yarn package manager

### Installation

```bash
npm install
```

### Development

Start the development server with Turbopack:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Build

Create a production build:

```bash
npm run build
```

### Run Production Build

```bash
npm start
```

### Linting

```bash
npm run lint
```

## Project Structure

```
frontend/
├── app/                    # App Router directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # Reusable React components
├── lib/                   # Utility functions and helpers
├── types/                 # TypeScript type definitions
├── public/                # Static assets
└── package.json
```

## Best Practices

- Use TypeScript for type safety
- Leverage Server Components by default
- Use Client Components (`'use client'`) only when needed
- Organize components by feature or domain
- Keep utility functions in the `lib/` directory
- Define shared types in the `types/` directory

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
