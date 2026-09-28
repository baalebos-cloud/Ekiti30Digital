/**
 * Public contributor signup: forwards to the backend's POST /api/auth/signup.
 *
 * Responses the form relies on:
 *   201 { status: "pending" }             account created, awaiting approval
 *   409 { detail }                        email already registered
 *   422 { errors: { field: message } }    validation failed (readable messages;
 *                                         the backend's raw 422 echoes the
 *                                         submitted password, so it's never relayed)
 *   502/504 { detail }                    backend failed or unreachable
 *
 * TODO(before launch): public and unthrottled, like the backend endpoint it
 * calls — add rate limiting before real traffic.
 */

import { API_URL } from "@/lib/config";
import { FIELD_LABELS, type SignupErrors, type SignupField } from "@/lib/signup";

type PydanticError = { loc?: unknown[]; msg?: string; type?: string; ctx?: Record<string, unknown> };

function readableErrors(detail: unknown): SignupErrors {
  const errors: SignupErrors = {};
  if (!Array.isArray(detail)) return errors;
  for (const item of detail as PydanticError[]) {
    const field = item.loc?.at(-1);
    if (field !== "name" && field !== "email" && field !== "password") continue;
    const label = FIELD_LABELS[field as SignupField];
    let message: string;
    if (item.type === "string_too_short") message = `${label} must be at least ${item.ctx?.min_length} characters.`;
    else if (item.type === "string_too_long") message = `${label} must be at most ${item.ctx?.max_length} characters.`;
    else if (item.msg?.startsWith("Value error, ")) message = `${label} ${item.msg.slice("Value error, ".length)}.`;
    else message = `${label} isn't valid.`;
    errors[field as SignupField] ??= message;
  }
  return errors;
}

export async function POST(request: Request) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return Response.json({ detail: "Request body must be JSON" }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Only the fields the backend expects.
      body: JSON.stringify({ name: body.name, email: body.email, password: body.password }),
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    });
  } catch {
    return Response.json({ detail: "The signup service can't be reached" }, { status: 504 });
  }

  const data: unknown = await upstream.json().catch(() => null);
  const detail = (data as { detail?: unknown } | null)?.detail;

  if (upstream.status === 201) return Response.json({ status: "pending" }, { status: 201 });
  if (upstream.status === 409) {
    return Response.json({ detail: typeof detail === "string" ? detail : "Email already registered" }, { status: 409 });
  }
  if (upstream.status === 422) return Response.json({ errors: readableErrors(detail) }, { status: 422 });
  return Response.json({ detail: "Signup failed" }, { status: 502 });
}
