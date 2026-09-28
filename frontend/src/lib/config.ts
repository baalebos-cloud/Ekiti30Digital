// Base URL of the FastAPI backend, for server-side calls. No trailing slash.
export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
