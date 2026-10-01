"use client";

import { Fragment } from "react";

import { SectionNotice, useHomepage } from "@/components/homepage/HomepageContent";
import { PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";
import { parseHeadline, type Hero as HeroContent } from "@/lib/homepage";

// The board's three fixed polaroid slots, in position order.
const POLAROIDS = ["p1", "p2", "p3"];

function Headline({ text }: { text: string }) {
  const lines = parseHeadline(text);
  return (
    <h1 className="hero-title">
      {lines.map((parts, i) => (
        <Fragment key={i}>
          {i > 0 && <br />}
          {parts.map((part, j) => (part.emphasis ? <em key={j}>{part.text}</em> : <Fragment key={j}>{part.text}</Fragment>))}
        </Fragment>
      ))}
    </h1>
  );
}

function HeroBody({ hero }: { hero: HeroContent }) {
  return (
    <>
      <div>
        <div className="eyebrow-row">
          <span className="eyebrow-dot"></span> {hero.eyebrow}
        </div>
        <Headline text={hero.headline} />
        <p className="hero-sub">{hero.subtitle}</p>
        <div className="hero-actions">
          <a className="btn-primary" href={hero.primaryCta.href}>
            {hero.primaryCta.label}
          </a>
          <a className="btn-secondary" href={hero.secondaryCta.href}>
            {hero.secondaryCta.label}
          </a>
        </div>
        {hero.facts.length > 0 && (
          <dl className="hero-facts">
            {hero.facts.map((fact) => (
              <div key={fact.label}>
                <dt>{fact.label}</dt>
                <dd>{fact.value}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>

      {hero.images.length > 0 && (
        <div className="board">
          {hero.images.slice(0, POLAROIDS.length).map((image, i) => (
            <div className={`polaroid ${POLAROIDS[i]}`} key={image.id}>
              <div className="pin"></div>
              <div className="frame">
                {image.imageUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary image
                  <img src={image.imageUrl} alt={image.caption} />
                ) : (
                  <PlaceholderIcon name={image.placeholderIcon} variant="hero" />
                )}
              </div>
              <div className="cap">{image.caption}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

function HeroSkeleton() {
  return (
    <>
      <div aria-busy="true" aria-label="Loading">
        <div className="skeleton mb-[18px] h-4 w-72 max-w-full rounded" />
        <div className="skeleton mb-3 h-10 w-64 max-w-full rounded md:h-12" />
        <div className="skeleton mb-[18px] h-10 w-80 max-w-full rounded md:h-12" />
        <div className="mb-[22px] flex max-w-[44ch] flex-col gap-2">
          <div className="skeleton h-4 rounded" />
          <div className="skeleton h-4 rounded" />
          <div className="skeleton h-4 w-2/3 rounded" />
        </div>
        <div className="flex flex-wrap gap-3.5">
          <div className="skeleton h-[46px] w-56 rounded-md" />
          <div className="skeleton h-[46px] w-52 rounded-md" />
        </div>
      </div>
      <div className="board" aria-hidden="true">
        {POLAROIDS.map((slot) => (
          <div className={`polaroid ${slot}`} key={slot}>
            <div className="frame skeleton" />
            <div className="cap">&nbsp;</div>
          </div>
        ))}
      </div>
    </>
  );
}

export default function Hero() {
  const { state, retry } = useHomepage();
  return (
    <section className="hero">
      <div className="wrap hero-inner">
        {state.status === "loading" ? (
          <HeroSkeleton />
        ) : state.status === "ready" && state.content.hero ? (
          <HeroBody hero={state.content.hero} />
        ) : (
          <div>
            <h1 className="hero-title">Welcome home.</h1>
            {state.status === "error" ? (
              <SectionNotice onRetry={retry}>We couldn&apos;t load this part of the page just now.</SectionNotice>
            ) : (
              <p className="hero-sub">Ekiti State at 30, 1996–2026.</p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
