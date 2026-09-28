"use client";

import { ReviewActions } from "@/components/review/ReviewActions";
import { formatDate } from "@/lib/review";
import { folderLabel, RIGHTS_OPTIONS, type AssetRecord } from "@/lib/uploads";

type Props = {
  asset: AssetRecord;
  onReview: (action: "approve" | "reject", reason?: string) => Promise<string | null>;
};

function rightsLabel(value: string): string {
  return RIGHTS_OPTIONS.find((r) => r.value === value)?.label ?? value;
}

/** One pending upload: preview, every submitted detail, and the review controls. */
export function MediaReviewCard({ asset, onReview }: Props) {
  const url = asset.cloudinary_url;
  const isVideo = url?.includes("/video/upload/") ?? false;

  const details: [string, string | null][] = [
    ["Contributor", asset.contributor],
    ["Rights", rightsLabel(asset.rights_status)],
    ["LGA", asset.location_lga],
    ["Source", asset.source],
    ["Related ID", asset.related_content_id],
  ];

  return (
    <article className="review-card">
      <div className="review-media">
        {url ? (
          isVideo ? (
            <video src={url} controls muted playsInline preload="metadata" />
          ) : (
            <a href={url} target="_blank" rel="noreferrer" title="Open full size in a new tab">
              {/* eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary preview, size varies */}
              <img src={url} alt={asset.description ?? `Upload #${asset.id}`} loading="lazy" />
            </a>
          )
        ) : (
          <div className="review-media-missing">
            <span aria-hidden="true">◌</span>
            File never finished uploading
          </div>
        )}
        <span className="review-folder">{folderLabel(asset.folder)}</span>
      </div>

      <div className="flex flex-1 flex-col gap-4 p-5">
        <div>
          <p className={`font-display text-[17px] leading-snug ${asset.description ? "" : "italic text-ink-soft"}`}>
            {asset.description ?? "No description given"}
          </p>
          <p className="mt-1 text-xs text-ink-soft">
            #{asset.id} · submitted {formatDate(asset.created_at)}
          </p>
        </div>

        <dl className="review-details">
          {details.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd className={value ? "" : "is-empty"}>{value ?? "—"}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-auto border-t border-dashed border-line pt-4">
          <ReviewActions
            noun="upload"
            reasonExamples="e.g. Rights unclear, image too blurry, duplicate of an earlier upload"
            approveBlockedReason={url ? undefined : "Nothing to approve — reject it to clear it."}
            onReview={onReview}
          />
        </div>
      </div>
    </article>
  );
}
