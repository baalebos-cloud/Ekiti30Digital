"use client";

import { useCallback, useEffect, useState } from "react";

import type { ContentKind, ContentResponse } from "@/lib/content";

export type ContentState<T> =
  | { status: "loading" }
  | { status: "error" }
  | ({ status: "ready" } & ContentResponse<T>);

async function load<T>(kind: ContentKind): Promise<ContentState<T>> {
  try {
    const response = await fetch(`/api/content/${kind}`);
    if (!response.ok) return { status: "error" };
    const data = (await response.json()) as ContentResponse<T>;
    return { status: "ready", ...data };
  } catch {
    return { status: "error" };
  }
}

/** Fetches one content feed through the Next.js route; retry() refetches. */
export function useContent<T>(kind: ContentKind) {
  const [state, setState] = useState<ContentState<T>>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    load<T>(kind).then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, [kind]);

  const retry = useCallback(async () => {
    setState({ status: "loading" });
    setState(await load<T>(kind));
  }, [kind]);

  return { state, retry };
}
