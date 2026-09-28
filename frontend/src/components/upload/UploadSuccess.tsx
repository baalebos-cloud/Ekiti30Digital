"use client";

import { motion } from "motion/react";
import Link from "next/link";

import { SuccessCheck } from "@/components/ui/SuccessCheck";
import { folderLabel, type AssetRecord } from "@/lib/uploads";

type Props = {
  asset: AssetRecord;
  previewUrl: string | null;
  video: boolean;
  fileName: string;
  onAnother: () => void;
};

// Brand-color confetti that bursts out from behind the checkmark.
const BURST = ["--forest", "--gold", "--rust", "--teal", "--forest-2", "--gold-soft"].flatMap((color, i) => [
  { color, angle: i * 60 + 12, distance: 46 },
  { color, angle: i * 60 + 42, distance: 34 },
]);

export function UploadSuccess({ asset, previewUrl, video, fileName, onAnother }: Props) {
  const caption = asset.description?.trim() || asset.location_lga || fileName;

  return (
    <motion.div
      key="success"
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="grid items-center gap-9 py-4 sm:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]"
      role="status"
    >
      {/* The upload, pinned to the memory board like the homepage collage */}
      <motion.figure
        className="upload-polaroid mx-auto w-full max-w-[260px]"
        initial={{ opacity: 0, y: 40, rotate: -14 }}
        animate={{ opacity: 1, y: 0, rotate: -3 }}
        transition={{ type: "spring", stiffness: 140, damping: 14, delay: 0.1 }}
      >
        <motion.span
          className="pin"
          initial={{ scale: 0, y: -12 }}
          animate={{ scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 500, damping: 14, delay: 0.55 }}
        />
        <div className="frame">
          {previewUrl &&
            (video ? (
              <video src={previewUrl} muted playsInline autoPlay loop />
            ) : (
              // eslint-disable-next-line @next/next/no-img-element -- local blob preview
              <img src={previewUrl} alt="" />
            ))}
        </div>
        <figcaption className="cap">{caption}</figcaption>
      </motion.figure>

      <div className="text-center sm:text-left">
        <div className="relative inline-block">
          {BURST.map((dot, i) => (
            <motion.span
              key={i}
              aria-hidden="true"
              className="absolute left-1/2 top-1/2 h-2 w-2 rounded-full"
              style={{ background: `var(${dot.color})`, marginLeft: -4, marginTop: -4 }}
              initial={{ x: 0, y: 0, scale: 0, opacity: 1 }}
              animate={{
                x: Math.cos((dot.angle * Math.PI) / 180) * dot.distance,
                y: Math.sin((dot.angle * Math.PI) / 180) * dot.distance,
                scale: [0, 1.2, 0.9],
                opacity: [1, 1, 0],
              }}
              transition={{ duration: 0.9, delay: 0.3, ease: "easeOut" }}
            />
          ))}
          <SuccessCheck size={52} />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.4 }}
        >
          <h2 className="mt-4 font-display text-3xl font-medium tracking-tight">
            Ẹ ṣeun — <em className="text-forest-2">thank you!</em>
          </h2>
          <p className="mt-2 text-ink-soft">
            Your {video ? "video" : "photo"} is safely in and waiting for the review team. Nothing
            appears publicly until an admin approves it.
          </p>

          <dl className="detail-list text-left">
            <dt>Status</dt>
            <dd>
              <span className="status-pill">Awaiting review</span>
            </dd>
            <dt>Collection</dt>
            <dd>{folderLabel(asset.folder)}</dd>
            <dt>Reference</dt>
            <dd className="tabular-nums">#{asset.id}</dd>
          </dl>

          <div className="mt-7 flex flex-wrap justify-center gap-3 sm:justify-start">
            <motion.button
              type="button"
              onClick={onAnother}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.97 }}
              className="btn-primary"
            >
              Share another
            </motion.button>
            <Link href="/" className="btn-secondary">
              Back to home
            </Link>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
