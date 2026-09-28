"use client";

import { useEffect, useRef, useState } from "react";

// Pixels per second. Slow enough to read names as they pass.
const SPEED = 28;
// How long after a manual scroll/drag before auto-scrolling resumes.
const RESUME_AFTER_MS = 2500;

/**
 * A horizontally scrollable row that drifts on its own, looping forever.
 *
 * It stays a normal scroll container, so people can still scroll it by hand;
 * hovering, focusing or scrolling it pauses the drift. The children are
 * rendered twice so the loop is seamless — the copy is hidden from screen
 * readers and keyboard focus. With "reduce motion" on it doesn't move and
 * renders the children once.
 */
export function AutoScrollRow({ className, children }: { className: string; children: React.ReactNode }) {
  const row = useRef<HTMLDivElement>(null);
  const copy = useRef<HTMLDivElement>(null);
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setAnimate(!media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    const el = row.current;
    if (!animate || !el) return;

    let hovered = false;
    let focused = false;
    let visible = true;
    let resumeAt = 0;
    let position = el.scrollLeft;
    let lastSet = el.scrollLeft;
    let lastTime = performance.now();
    let frame = 0;

    // Distance from the first copy of the children to the second (both
    // share an offset parent, so the difference is exact).
    const period = () => {
      const first = el.firstElementChild as HTMLElement | null;
      return first && copy.current ? copy.current.offsetLeft - first.offsetLeft : 0;
    };

    const tick = (now: number) => {
      const dt = Math.min(now - lastTime, 100) / 1000;
      lastTime = now;

      // A scroll we didn't make means someone is scrolling by hand.
      if (Math.abs(el.scrollLeft - lastSet) > 2) {
        position = el.scrollLeft;
        resumeAt = now + RESUME_AFTER_MS;
      }

      if (!hovered && !focused && visible && now >= resumeAt) {
        position += SPEED * dt;
      }
      const loop = period();
      if (loop > 0 && position >= loop) position -= loop;

      el.scrollLeft = position;
      lastSet = el.scrollLeft;
      frame = requestAnimationFrame(tick);
    };

    const pauseForInteraction = () => {
      resumeAt = performance.now() + RESUME_AFTER_MS;
    };
    const onEnter = () => (hovered = true);
    const onLeave = () => (hovered = false);
    const onFocusIn = () => (focused = true);
    const onFocusOut = () => (focused = false);
    const observer = new IntersectionObserver(([entry]) => (visible = entry.isIntersecting));

    el.addEventListener("pointerenter", onEnter);
    el.addEventListener("pointerleave", onLeave);
    el.addEventListener("focusin", onFocusIn);
    el.addEventListener("focusout", onFocusOut);
    el.addEventListener("pointerdown", pauseForInteraction);
    el.addEventListener("wheel", pauseForInteraction, { passive: true });
    el.addEventListener("touchstart", pauseForInteraction, { passive: true });
    observer.observe(el);
    frame = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      el.removeEventListener("pointerenter", onEnter);
      el.removeEventListener("pointerleave", onLeave);
      el.removeEventListener("focusin", onFocusIn);
      el.removeEventListener("focusout", onFocusOut);
      el.removeEventListener("pointerdown", pauseForInteraction);
      el.removeEventListener("wheel", pauseForInteraction);
      el.removeEventListener("touchstart", pauseForInteraction);
    };
  }, [animate]);

  return (
    <div ref={row} className={`${className} ${animate ? "is-auto-scrolling" : ""}`}>
      <div className="auto-scroll-set">{children}</div>
      {animate && (
        <div ref={copy} className="auto-scroll-set" aria-hidden="true" inert>
          {children}
        </div>
      )}
    </div>
  );
}
