# EduMind Frontend

Next.js 16 frontend for the AI Learning Assistant Platform (FastAPI backend).

## Quick Start

```bash
cd Frontend
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

With Docker Compose (from repo root):

```bash
docker compose up
```

The frontend container uses `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` and `API_INTERNAL_URL=http://backend:8000/api/v1`.

## Environment Variables

| Variable | Scope | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | Browser | API base for Axios and SSE |
| `API_INTERNAL_URL` | Server only | API base for SSR fetch (Docker internal network) |

See [`.env.example`](.env.example) for per-environment values.

## Authentication Architecture

The backend delivers JWT tokens exclusively via **HttpOnly cookies**. The frontend never stores, reads, or sends tokens manually.

### What the frontend does

| Action | Implementation |
|--------|----------------|
| Login | `POST /auth/login` → cookies set by browser → `GET /auth/me` |
| Session restore | `AuthProvider.checkAuth()` calls `/auth/me` on mount |
| API calls | `apiClient` with `withCredentials: true` |
| Token refresh | Axios interceptor calls `POST /auth/refresh` on 401 |
| Logout | `POST /auth/logout` → backend revokes tokens and clears cookies |
| Route guards | `middleware.ts` (edge) + `dashboard-layout-client.tsx` (client) |

### What the frontend does NOT do

- Store `access_token` or `refresh_token` in `localStorage` / `sessionStorage`
- Set `Authorization: Bearer` headers from client-side token state
- Read cookie values in client JavaScript

### CSRF protection

Write requests authenticated via cookies are validated server-side using `Origin` / `Referer` headers against `BACKEND_CORS_ORIGINS`. No CSRF token is required on the frontend.

### Key files

```
src/
├── config/api.ts           # API URL configuration
├── services/api-client.ts # Axios instance + refresh interceptor
├── services/user.ts        # Auth API wrappers
├── providers/auth-provider.tsx
├── middleware.ts           # Edge route guard (UX only)
├── lib/auth-cookies.ts     # Cookie constants + JWT decode helpers
├── lib/server-api.ts       # SSR authenticated fetch
├── lib/safe-redirect.ts    # Post-login redirect validation
└── utils/api-error.ts      # FastAPI error message parser
```

## Project Structure

```
src/app/
├── (auth)/          # Login, register
├── (dashboard)/     # Student, teacher, admin workspaces
src/components/     # Role-scoped UI components
src/services/         # API abstraction layer
src/types/            # TypeScript contracts (mirrors backend schemas)
```

## Scripts

```bash
npm run dev      # Development server (webpack)
npm run build    # Production build (use --webpack if Turbopack conflicts)
npm run start    # Start production server
npm run lint     # ESLint
```

## Production (nginx)

When served behind the nginx reverse proxy at `https://localhost`, set:

```
NEXT_PUBLIC_API_URL=https://localhost/api/v1
```

Or use a relative path for same-origin requests:

```
NEXT_PUBLIC_API_URL=/api/v1
```

## Production Build (Docker)

The production Dockerfile accepts build-time API URLs:

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=/api/v1 \
  --build-arg API_INTERNAL_URL=http://backend:8000/api/v1 \
  -f Frontend/Dockerfile.prod \
  Frontend
```

`npm run build` uses webpack explicitly (required while custom webpack config is present).
