"use client";

import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";

import { ContentEditor } from "@/components/content-admin/ContentEditor";
import { ContentList } from "@/components/content-admin/ContentList";
import { CsvImport } from "@/components/content-admin/CsvImport";
import { EmptyState, ErrorState, LoadingState } from "@/components/review/SectionStates";
import { Spinner } from "@/components/ui/Spinner";
import { SuccessToast, useToast } from "@/components/ui/SuccessToast";
import {
  contentApi,
  CONTENT_ADMIN_KINDS,
  NOUN,
  recordKey,
  recordTitle,
  type ContentAdminKind,
  type ContentRecord,
} from "@/lib/contentAdmin";

type ListState =
  | { status: "loading" }
  | { status: "error"; message: string; signInAgain: boolean }
  | { status: "ready"; items: ContentRecord[] };

type View = { mode: "list" } | { mode: "edit"; record: ContentRecord } | { mode: "create" } | { mode: "import" };

const LABELS: Record<ContentAdminKind, string> = { lgas: "LGAs", timeline: "Timeline" };

function sortItems(kind: ContentAdminKind, items: ContentRecord[]): ContentRecord[] {
  const sortKey = (r: ContentRecord) => (kind === "lgas" ? recordKey(kind, r) : `${r.date_start}|${recordKey(kind, r)}`);
  return [...items].sort((a, b) => (sortKey(a) < sortKey(b) ? -1 : 1));
}

function useContentList(kind: ContentAdminKind) {
  const [state, setState] = useState<ListState>({ status: "loading" });

  const load = useCallback(async (): Promise<ListState> => {
    const result = await contentApi.list(kind);
    return result.ok
      ? { status: "ready", items: sortItems(kind, result.data) }
      : { status: "error", message: result.message, signInAgain: result.status === 401 };
  }, [kind]);

  useEffect(() => {
    let cancelled = false;
    load().then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, [load]);

  const reload = useCallback(async () => {
    setState({ status: "loading" });
    setState(await load());
  }, [load]);

  const replace = useCallback(
    (saved: ContentRecord, previousKey: string | null) =>
      setState((s) =>
        s.status !== "ready"
          ? s
          : {
              ...s,
              items: sortItems(kind, [
                ...s.items.filter((i) => recordKey(kind, i) !== (previousKey ?? recordKey(kind, saved))),
                saved,
              ]),
            },
      ),
    [kind],
  );

  const remove = useCallback(
    (key: string) =>
      setState((s) => (s.status === "ready" ? { ...s, items: s.items.filter((i) => recordKey(kind, i) !== key) } : s)),
    [kind],
  );

  return { state, reload, replace, remove };
}

/** The "Manage content" tab: edit, add, delete and import LGAs and timeline events. */
export function ContentManager() {
  const [kind, setKind] = useState<ContentAdminKind>("lgas");
  const lgas = useContentList("lgas");
  const timeline = useContentList("timeline");
  const lists = { lgas, timeline };
  const [views, setViews] = useState<Record<ContentAdminKind, View>>({ lgas: { mode: "list" }, timeline: { mode: "list" } });
  const { toast, show } = useToast();

  const list = lists[kind];
  const view = views[kind];
  const setView = (next: View) => {
    setViews((v) => ({ ...v, [kind]: next }));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  async function remove(record: ContentRecord): Promise<string | null> {
    const key = recordKey(kind, record);
    const result = await contentApi.remove(kind, key);
    if (!result.ok) return result.message;
    list.remove(key);
    show(`Deleted · ${recordTitle(kind, record)}`);
    return null;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Content type" className="flex gap-1 rounded-full border border-line bg-bg-raised p-1">
          {CONTENT_ADMIN_KINDS.map((k) => (
            <button
              key={k}
              type="button"
              role="tab"
              aria-selected={kind === k}
              onClick={() => setKind(k)}
              className={`relative rounded-full px-4 py-1.5 text-sm font-semibold transition-colors ${kind === k ? "text-white" : "text-ink-soft hover:text-ink"}`}
            >
              {kind === k && (
                <motion.span
                  layoutId="content-kind-pill"
                  className="absolute inset-0 rounded-full bg-forest"
                  transition={{ type: "spring", stiffness: 420, damping: 34 }}
                />
              )}
              <span className="relative">{LABELS[k]}</span>
            </button>
          ))}
        </div>

        {view.mode === "list" && (
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" onClick={() => list.reload()} disabled={list.state.status === "loading"} className="link-btn flex items-center gap-1.5">
              {list.state.status === "loading" && <Spinner size={12} />}
              Refresh
            </button>
            <button type="button" className="btn-secondary btn-flex btn-sm" onClick={() => setView({ mode: "import" })}>
              Import CSV
            </button>
            <motion.button
              type="button"
              className="btn-primary btn-flex btn-sm"
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setView({ mode: "create" })}
            >
              + Add {NOUN[kind].one}
            </motion.button>
          </div>
        )}
      </div>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={`${kind}-${view.mode}-${view.mode === "edit" ? recordKey(kind, view.record) : ""}`}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
        >
          {view.mode === "edit" || view.mode === "create" ? (
            <ContentEditor
              kind={kind}
              record={view.mode === "edit" ? view.record : null}
              onCancel={() => setView({ mode: "list" })}
              onSaved={(saved, previousKey) => {
                list.replace(saved, previousKey);
                show(`${previousKey === null ? "Added" : "Saved"} · ${recordTitle(kind, saved)}`);
                setView({ mode: "list" });
              }}
            />
          ) : view.mode === "import" ? (
            <CsvImport
              kind={kind}
              onClose={() => setView({ mode: "list" })}
              onImported={(summary) => {
                list.reload();
                show(`Imported · ${summary.created.length} added, ${summary.updated.length} updated`);
              }}
            />
          ) : list.state.status === "loading" ? (
            <LoadingState variant="rows" />
          ) : list.state.status === "error" ? (
            <ErrorState message={list.state.message} signInAgain={list.state.signInAgain} onRetry={list.reload} />
          ) : list.state.items.length === 0 ? (
            <EmptyState
              title={`No ${NOUN[kind].many} yet`}
              body={`Add one, or import the ${kind === "lgas" ? "LGA" : "timeline"} CSV to load them all at once.`}
            />
          ) : (
            <ContentList kind={kind} items={list.state.items} onEdit={(record) => setView({ mode: "edit", record })} onDelete={remove} />
          )}
        </motion.div>
      </AnimatePresence>

      <SuccessToast toast={toast} />
    </div>
  );
}
