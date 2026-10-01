"use client";

import { motion } from "motion/react";

import { PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";
import { ICON_LABELS, PLACEHOLDER_ICONS, type PlaceholderIconName } from "@/lib/homepage";

/** Choose a card's placeholder icon: a radio group drawn as the icons themselves. */
export function IconPicker({
  id,
  value,
  onChange,
  describedBy,
}: {
  id: string;
  value: PlaceholderIconName;
  onChange: (value: PlaceholderIconName) => void;
  describedBy?: string;
}) {
  return (
    <div role="radiogroup" aria-labelledby={`${id}-label`} aria-describedby={describedBy} className="icon-picker">
      {PLACEHOLDER_ICONS.map((name) => {
        const selected = name === value;
        return (
          <label key={name} className={`icon-choice ${selected ? "is-selected" : ""}`} title={ICON_LABELS[name]}>
            <input
              type="radio"
              name={id}
              value={name}
              checked={selected}
              onChange={() => onChange(name)}
              className="sr-only"
            />
            {selected && (
              <motion.span
                layoutId={`${id}-selected`}
                className="icon-choice-ring"
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              />
            )}
            <PlaceholderIcon name={name} />
            <span className="sr-only">{ICON_LABELS[name]}</span>
          </label>
        );
      })}
    </div>
  );
}
