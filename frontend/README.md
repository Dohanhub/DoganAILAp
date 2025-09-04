# DoganAI Frontend

React + Vite + TypeScript application for the DoganAI Compliance Kit.

## Quick Start

- Node 20+ required. Install deps:
  - Using npm: `npm install`
  - Or pnpm (preferred at repo root): `pnpm --filter ./frontend i`
- Development: `npm run dev`
- Build: `npm run build`
- Preview: `npm run preview`

## Linting & Formatting

- ESLint config: `eslint.config.js`
- Prettier config: `.prettierrc.json`
- Run lint: `npm run lint` (or `npm run lint:fix`)

## Testing

- Vitest config: `vitest.config.ts`
- Run tests: `npm run test` (UI: `npm run test:ui`)

## Storybook

- Config in `.storybook/`
- Start: `npm run storybook`

## Environment Variables

- Public variables must be prefixed with `VITE_`.
- Files provided:
  - `.env` and `.env.local` (safe defaults)
  - `.env.example` (copy to `.env` and adjust)
- Common keys:
  - `VITE_API_URL` — backend API base URL
  - `VITE_GATEWAY_URL` — gateway base URL

## Notes on Package Managers

The monorepo declares a pnpm workspace at the root. For the isolated frontend CI we use `npm install`. In local dev you can use either npm in `frontend/` or pnpm from the repo root with `--filter ./frontend`.

