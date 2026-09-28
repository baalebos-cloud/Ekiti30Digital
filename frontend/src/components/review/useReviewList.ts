"use client";

import { useCallback, useEffect, useState } from "react";

import { reviewErrorMessage, type ReviewKind } from "@/lib/review";

export type ListState<T> =
  | { status: "loading" }
  | { status: "error"; message: string; signInAgain: boolean }
  | { status: "ready"; items: T[] };

async function fetchPending<T>(kind: ReviewKind): Promise<ListState<T>> {
  try {
    const response = await fetch(`/api/admin/${kind}/pending`, { cache: "no-store" });
    const data: unknown = await response.json().catch(() => null);
    if (response.ok && Array.isArray(data)) return { status: "ready", items: data as T[] };
    return {
      status: "error",
      message: reviewErrorMessage(response.ok ? 500 : response.status),
      signInAgain: response.status === 401,
    };
  } catch {
    return { status: "error", message: reviewErrorMessage(null), signInAgain: false };
  }
}

/** A pending-review list: loads on mount, reloads on demand, drops reviewed items. */
export function useReviewList<T extends { id: number }>(kind: ReviewKind) {
  const [state, setState] = useState<ListState<T>>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetchPending<T>(kind).then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, [kind]);

  const reload = useCallback(async () => {
    setState({ status: "loading" });
    setState(await fetchPending<T>(kind));
  }, [kind]);

  const remove = useCallback((id: number) => {
    setState((s) => (s.status === "ready" ? { ...s, items: s.items.filter((i) => i.id !== id) } : s));
  }, []);

  return { state, reload, remove };
}

/** Approve or reject one item. Resolves to an error message, or null on success. */
export async function sendReview(
  kind: ReviewKind,
  id: number,
  action: "approve" | "reject",
  reason?: string,
): Promise<string | null> {
  try {
    const response = await fetch(`/api/admin/${kind}/${id}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(action === "reject" ? { rejection_reason: reason } : {}),
    });
    if (response.ok) return null;
    const data = (await response.json().catch(() => null)) as { detail?: unknown } | null;
    return reviewErrorMessage(response.status, data?.detail);
  } catch {
    return reviewErrorMessage(null);
  }
}
