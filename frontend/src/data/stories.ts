// Shape of a published citizen story, as the /api/content/stories feed
// returns it. Fields follow the public presentation in
// 11_Citizen_Stories/MY_EKITI_STORY_SPEC.md section 9. The backend's
// GET /api/stories should return { "stories": [CitizenStory, ...] }.

export type CitizenStory = {
  id: string;
  title: string;
  /** The public credit line, after the contributor's credit choice. */
  sharedBy: string;
  lga: string;
  period?: string;
  language?: "English" | "Yoruba";
  text: string;
  photo?: { caption: string; tone: "gold" | "forest" | "teal" | "rust" };
  published?: string;
};
