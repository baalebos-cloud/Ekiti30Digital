// Shape of a published citizen vision, as the /api/content/vision2056 feed
// returns it. Fields and categories follow 12_Ekiti_2056/EKITI_2056_SPEC.md
// (sections 5 and 8). The backend's GET /api/vision2056 should return
// { "visions": [CitizenVision, ...] }.

export type VisionCategory =
  | "Education"
  | "Health"
  | "Agriculture"
  | "Technology & Innovation"
  | "Youth & Entrepreneurship"
  | "Economy & Jobs"
  | "Infrastructure & Environment"
  | "Culture, Heritage & Tourism"
  | "Governance & Community Development"
  | "Other";

export type CitizenVision = {
  id: string;
  headline: string;
  sharedBy: string;
  lga?: string;
  category: VisionCategory | string;
  language?: "English" | "Yoruba";
  vision: string;
  whyItMatters?: string;
  published?: string;
};
