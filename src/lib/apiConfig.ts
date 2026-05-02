// S001-NFR-005 Phase 1.5 — single-origin via nginx reverse proxy.
//
// API_BASE_URL defaults to "" (relative URLs) so the SPA emits paths like
// `/api/foo` and `/ws/chat/...` that the frontend container's nginx proxies
// to the backend service. No hardcoded localhost in the bundle.
//
// VITE_API_BASE_URL remains an escape hatch for `npm run dev` against a
// non-default backend (e.g. cross-origin dev mode). Empty default keeps
// the production bundle environment-agnostic.

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

// Runtime-derived WebSocket origin. Empty during SSR/build (no `window`).
// In the browser: same origin as the page, with http→ws / https→wss.
export const WS_BASE_URL =
  typeof window === "undefined"
    ? ""
    : window.location.origin.replace(/^http/, "ws");
