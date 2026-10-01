"use client";

/**
 * One homepage list (leaders, landmarks, moments or hero photos): in homepage
 * order, with reordering, add, edit and delete. A move is saved at once (the
 * whole new order, POST .../reorder) and undone on screen if it fails.
 */

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useCallback, useEffect, useState } from "react";

import { AuditLine } from "@/components/content-admin/AuditLine";
import { ItemEditor } from "@/components/homepage-admin/ItemEditor";
import { LeaderIcon, PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";
import { EmptyState, ErrorState, LoadingState } from "@/components/review/SectionStates";
import { Spinner } from "@/components/ui/Spinner";
import type { PlaceholderIconName } from "@/lib/homepage";
import { homepageApi, LIST_CONFIG, type HomepageList, type ListRecord, type MomentRecord } from "@/lib/homepageAdmin";

type ListState =
  | { status: "loading" }
  | { status: "error"; message: string; signInAgain: boolean }
  | { status: "ready"; items: ListRecord[] };

type View = { mode: "list" } | { mode: "edit"; record: ListRecord } | { mode: "create" };

const byPosition = (items: ListRecord[]) => [...items].sort((a, b) => a.position - b.position || a.id - b.id);

export function ListManager({ list, onToast }: { list: HomepageList; onToast: (message: string) => void }) {
  const config = LIST_CONFIG[list];
  const [state, setState] = useState<ListState>({ status: "loading" });
  const [view, setView] = useState<View>({ mode: "list" });
  const [orderError, setOrderError] = useState<string | null>(null);
  const [moving, setMoving] = useState(false);

  const load = useCallback(async (): Promise<ListState> => {
    const result = await homepageApi.list(list);
    return result.ok
      ? { status: "ready", items: byPosition(result.data) }
      : { status: "error", message: result.message, signInAgain: result.status === 401 };
  }, [list]);

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

  function replace(saved: ListRecord) {
    setState((s) => (s.status === "ready" ? { ...s, items: byPosition([...s.items.filter((i) => i.id !== saved.id), saved]) } : s));
  }

  function open(next: View) {
    setView(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function move(index: number, by: -1 | 1) {
    if (state.status !== "ready") return;
    const before = state.items;
    const target = index + by;
    if (target < 0 || target >= before.length) return;
    const after = [...before];
    [after[index], after[target]] = [after[target], after[index]];
    setOrderError(null);
    setMoving(true);
    setState({ ...state, items: after });
    const result = await homepageApi.reorder(list, after.map((i) => i.id));
    setMoving(false);
    if (result.ok) {
      setState({ status: "ready", items: byPosition(result.data) });
    } else {
      setState({ status: "ready", items: before });
      setOrderError(`The new order wasn't saved: ${result.message}`);
    }
  }

  async function remove(record: ListRecord): Promise<string | null> {
    const result = await homepageApi.remove(list, record.id);
    if (!result.ok) return result.message;
    // The backend closes the gap in positions; reload to match it.
    setState(await load());
    onToast(`Deleted · ${config.title(record)}`);
    return null;
  }

  const full = config.max !== undefined && state.status === "ready" && state.items.length >= config.max;

  if (view.mode !== "list") {
    return (
      <ItemEditor
        list={list}
        record={view.mode === "edit" ? view.record : null}
        onCancel={() => open({ mode: "list" })}
        onSaved={(saved, created) => {
          replace(saved);
          onToast(`${created ? "Added" : "Saved"} · ${config.title(saved)}`);
          open({ mode: "list" });
        }}
        onRecordChanged={replace}
      />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-ink-soft">
          Shown on the homepage in this order.
          {config.max !== undefined && ` The hero has room for ${config.max}.`}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <button type="button" onClick={reload} disabled={state.status === "loading"} className="link-btn flex items-center gap-1.5">
            {state.status === "loading" && <Spinner size={12} />}
            Refresh
          </button>
          <motion.button
            type="button"
            className="btn-primary btn-flex btn-sm"
            whileHover={full ? undefined : { y: -1 }}
            whileTap={full ? undefined : { scale: 0.97 }}
            onClick={() => open({ mode: "create" })}
            disabled={full || state.status !== "ready"}
            title={full ? `There can be at most ${config.max}; delete one first.` : undefined}
          >
            + Add {config.noun.one}
          </motion.button>
        </div>
      </div>

      <AnimatePresence initial={false}>
        {orderError && (
          <motion.div key="order-error" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            <div className="alert alert-error" role="alert">
              <span aria-hidden="true">●</span>
              <span>{orderError}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {state.status === "loading" ? (
        <LoadingState variant="rows" />
      ) : state.status === "error" ? (
        <ErrorState message={state.message} signInAgain={state.signInAgain} onRetry={reload} />
      ) : state.items.length === 0 ? (
        <EmptyState title={`No ${config.noun.many} yet`} body={`Add one and it appears on the homepage straight away.`} />
      ) : (
        <ol className="flex flex-col gap-3" aria-label={`${config.label}, in homepage order`}>
          {state.items.map((item, index) => (
            <motion.li key={item.id} layout="position" transition={{ type: "spring", stiffness: 500, damping: 40 }}>
              <ItemRow
                list={list}
                item={item}
                index={index}
                count={state.items.length}
                moving={moving}
                onMove={(by) => move(index, by)}
                onEdit={() => open({ mode: "edit", record: item })}
                onDelete={() => remove(item)}
              />
            </motion.li>
          ))}
        </ol>
      )}
    </div>
  );
}

function Thumb({ list, item }: { list: HomepageList; item: ListRecord }) {
  if (item.image_url) {
    // eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary thumbnail
    return <img src={item.image_url} alt="" className={`homepage-thumb ${list === "leaders" || list === "moments" ? "is-round" : ""}`} loading="lazy" />;
  }
  const icon = "placeholder_icon" in item ? (item.placeholder_icon as PlaceholderIconName) : null;
  const anchor = list === "moments" && (item as MomentRecord).is_anchor;
  return (
    <span
      className={`homepage-thumb homepage-thumb-placeholder ${list === "leaders" || list === "moments" ? "is-round" : ""} ${anchor ? "is-anchor" : ""}`}
      title="No image yet: the homepage shows this placeholder"
      aria-hidden="true"
    >
      {icon ? <PlaceholderIcon name={icon} /> : <LeaderIcon />}
    </span>
  );
}

function ItemRow({
  list,
  item,
  index,
  count,
  moving,
  onMove,
  onEdit,
  onDelete,
}: {
  list: HomepageList;
  item: ListRecord;
  index: number;
  count: number;
  moving: boolean;
  onMove: (by: -1 | 1) => void;
  onEdit: () => void;
  onDelete: () => Promise<string | null>;
}) {
  const config = LIST_CONFIG[list];
  const controls = useAnimationControls();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const title = config.title(item);
  const subtitle = config.subtitle(item);

  async function confirmDelete() {
    setBusy(true);
    setError(null);
    const failure = await onDelete();
    if (failure) {
      setBusy(false);
      setError(failure);
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
    }
  }

  return (
    <motion.div animate={controls} className="review-row">
      <div className="flex min-w-0 flex-[1_1_260px] items-center gap-3.5">
        <div className="flex flex-col items-center gap-0.5" role="group" aria-label={`Move ${title}`}>
          <button
            type="button"
            className="order-btn"
            onClick={() => onMove(-1)}
            disabled={moving || index === 0}
            aria-label={`Move ${title} up`}
          >
            <Arrow direction="up" />
          </button>
          <span className="text-xs font-semibold tabular-nums text-ink-soft" aria-hidden="true">
            {index + 1}
          </span>
          <button
            type="button"
            className="order-btn"
            onClick={() => onMove(1)}
            disabled={moving || index === count - 1}
            aria-label={`Move ${title} down`}
          >
            <Arrow direction="down" />
          </button>
        </div>
        <Thumb list={list} item={item} />
        <div className="flex min-w-0 flex-col items-start gap-1">
          <p className="flex flex-wrap items-center gap-2 font-display text-lg leading-tight">
            {title}
            {list === "moments" && (item as MomentRecord).is_anchor && <span className="label-pill">Anchor</span>}
          </p>
          {subtitle && <p className="text-sm text-ink-soft">{subtitle}</p>}
          <AuditLine updatedBy={item.updated_by} updatedAt={item.updated_at} />
        </div>
      </div>

      <div className="review-row-actions flex flex-col gap-2">
        <AnimatePresence initial={false}>
          {error && (
            <motion.div key="error" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
              <div className="alert alert-error" role="alert">
                <span aria-hidden="true">●</span>
                <span>{error}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        {confirming ? (
          <div className="flex flex-col gap-2">
            <p className="text-sm">
              Delete <strong>{title}</strong>? It disappears from the homepage at once. This can&apos;t be undone here.
            </p>
            <div className="flex flex-wrap justify-end gap-2">
              <button type="button" className="btn-secondary btn-flex btn-sm" disabled={busy} onClick={() => setConfirming(false)} autoFocus>
                Keep it
              </button>
              <button type="button" className="btn-primary btn-flex btn-sm" disabled={busy} onClick={confirmDelete}>
                {busy ? (
                  <>
                    <Spinner size={14} /> Deleting…
                  </>
                ) : (
                  `Delete ${config.noun.one}`
                )}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-wrap items-center justify-end gap-3">
            <button type="button" className="link-btn is-danger" onClick={() => setConfirming(true)}>
              Delete
            </button>
            <motion.button type="button" className="btn-secondary btn-flex btn-sm" whileHover={{ y: -1 }} whileTap={{ scale: 0.97 }} onClick={onEdit}>
              Edit
            </motion.button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function Arrow({ direction }: { direction: "up" | "down" }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={direction === "up" ? "M6 15l6-6 6 6" : "M6 9l6 6 6-6"} />
    </svg>
  );
}
