import { Reveal } from "@/components/ui/Reveal";
import type { CitizenStory } from "@/data/stories";

/** Published citizen stories, laid out as the spec's public presentation. */
export function StoryList({ stories }: { stories: CitizenStory[] }) {
  return (
    <div className="story-grid">
      {stories.map((story, i) => (
        <Reveal key={story.id} as="article" delay={(i % 2) * 0.08} className="story-card">
          {story.photo && (
            <figure className={`story-photo tone-${story.photo.tone}`}>
              <svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <circle cx="9" cy="10" r="1.6" />
                <path d="m21 16-5-5-8 8" />
              </svg>
              <figcaption>{story.photo.caption}</figcaption>
            </figure>
          )}
          <span className="label-pill">Citizen account</span>
          <h2 className="mt-3 font-display text-2xl font-medium leading-snug">{story.title}</h2>
          <p className="story-text">{story.text}</p>
          <div className="story-meta">
            <span className="font-semibold text-ink">{story.sharedBy}</span>
            <span>{[story.lga, story.period, story.language].filter(Boolean).join(" · ")}</span>
            {story.published && <span>Published {story.published}</span>}
          </div>
        </Reveal>
      ))}
    </div>
  );
}
