/**
 * Thin fetch wrapper around the backend. During dev, requests go to `/api/*`
 * and Vite proxies them to the FastAPI server (see vite.config.ts).
 *
 * Types in `schema.d.ts` are GENERATED from the backend OpenAPI schema:
 *   npm run gen:api
 * so the client and server never drift.
 */
const BASE = "/api";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}
