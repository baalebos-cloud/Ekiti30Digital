import { formatDate } from "@/lib/review";

/** Who last changed a record, and when. */
export function AuditLine({ updatedBy, updatedAt }: { updatedBy: string | null; updatedAt: string }) {
  return (
    <p className="text-xs text-ink-soft">
      {updatedBy ? (
        <>
          Last changed by <span className="font-semibold text-ink">{updatedBy}</span>
        </>
      ) : (
        // No verified identity: the initial load or the CLI script.
        <>Loaded by script — no admin recorded</>
      )}{" "}
      · {formatDate(updatedAt)}
    </p>
  );
}
