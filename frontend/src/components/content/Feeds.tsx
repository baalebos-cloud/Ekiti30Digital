"use client";

/**
 * The four content feeds: each fetches /api/content/{kind}, shows a
 * skeleton while loading, then the content, an empty state or an error.
 */

import Link from "next/link";

import {
  CardListSkeleton,
  ContentEmpty,
  ContentError,
  LgaGridSkeleton,
  TimelineSkeleton,
} from "@/components/content/ContentStates";
import { useContent } from "@/components/content/useContent";
import { LgaExplorer } from "@/components/explore/LgaExplorer";
import { StoryList } from "@/components/stories/StoryList";
import TimelineView from "@/components/TimelineView";
import { VisionBoard } from "@/components/vision/VisionBoard";
import type { Lga } from "@/data/lgas";
import type { CitizenStory } from "@/data/stories";
import type { TimelineEvent } from "@/data/timelineEvents";
import type { CitizenVision } from "@/data/visions";

export function TimelineFeed() {
  const { state, retry } = useContent<TimelineEvent>("timeline");

  if (state.status === "loading") return <TimelineSkeleton />;
  if (state.status === "error") {
    return (
      <div className="wrap content-section">
        <ContentError what="the timeline" onRetry={retry} />
      </div>
    );
  }
  if (state.items.length === 0) {
    return (
      <div className="wrap content-section">
        <ContentEmpty body="The 30-year timeline is being prepared. Verified events will appear here soon." />
      </div>
    );
  }

  const verified = state.items.filter((e) => e.status === "Verified").length;
  return (
    <>
      <div className="wrap">
        <dl className="tl-stats">
          <div>
            <dt>Events</dt>
            <dd>{state.items.length}</dd>
          </div>
          <div>
            <dt>Fully verified</dt>
            <dd>{verified}</dd>
          </div>
          <div>
            <dt>Themes</dt>
            <dd>{new Set(state.items.map((e) => e.category)).size}</dd>
          </div>
        </dl>
      </div>
      <TimelineView events={state.items} />
    </>
  );
}

export function ExploreFeed() {
  const { state, retry } = useContent<Lga>("lgas");

  if (state.status === "loading") return <LgaGridSkeleton />;
  if (state.status === "error") return <ContentError what="the local governments" onRetry={retry} />;
  if (state.items.length === 0) {
    return <ContentEmpty body="Profiles of Ekiti's 16 local governments are on their way." />;
  }
  return <LgaExplorer lgas={state.items} />;
}

export function StoriesFeed({ uploadHref }: { uploadHref: string }) {
  const { state, retry } = useContent<CitizenStory>("stories");

  if (state.status === "loading") return <CardListSkeleton className="story-grid" />;
  if (state.status === "error") return <ContentError what="stories" onRetry={retry} />;
  if (state.items.length === 0) {
    return (
      <ContentEmpty body="Stories are reviewed by the EKITI@30 team before they appear. The first ones will be published here soon.">
        <Link href={uploadHref} className="btn-primary btn-flex">
          Be one of the first to share
        </Link>
      </ContentEmpty>
    );
  }
  return <StoryList stories={state.items} />;
}

export function VisionFeed() {
  const { state, retry } = useContent<CitizenVision>("vision2056");

  if (state.status === "loading") return <CardListSkeleton className="vision-grid" />;
  if (state.status === "error") return <ContentError what="visions" onRetry={retry} />;
  if (state.items.length === 0) {
    return (
      <ContentEmpty body="Citizen visions for Ekiti's next thirty years will be published here once reviewed." />
    );
  }
  return <VisionBoard visions={state.items} />;
}
