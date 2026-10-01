"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

import type { HomepageContent } from "@/lib/homepage";

export type HomepageState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ready"; content: HomepageContent };

type Context = { state: HomepageState; retry: () => void };

const HomepageContext = createContext<Context | null>(null);

async function load(): Promise<HomepageState> {
  try {
    const response = await fetch("/api/homepage");
    if (!response.ok) return { status: "error" };
    return { status: "ready", content: (await response.json()) as HomepageContent };
  } catch {
    return { status: "error" };
  }
}

/** Fetches the homepage's content once, for every section inside it. */
export function HomepageProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<HomepageState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    load().then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const retry = useCallback(async () => {
    setState({ status: "loading" });
    setState(await load());
  }, []);

  return <HomepageContext.Provider value={{ state, retry }}>{children}</HomepageContext.Provider>;
}

export function useHomepage(): Context {
  const context = useContext(HomepageContext);
  if (!context) throw new Error("useHomepage must be used inside <HomepageProvider>");
  return context;
}

/**
 * What a section shows instead of its items: nothing yet, or a failed load
 * (with a retry). Quiet, in the section's own style, never an error page.
 */
export function SectionNotice({ children, onRetry }: { children: React.ReactNode; onRetry?: () => void }) {
  return (
    <div className="home-notice" role={onRetry ? "alert" : "status"}>
      <p>{children}</p>
      {onRetry && (
        <button type="button" className="home-notice-retry" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
