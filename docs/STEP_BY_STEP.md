# Step-by-Step Guide for Esther

A simple walkthrough, start to finish. For full technical details, see the main PRD tab.

## Step 1: Get the code and switch to your branch

1. If you don't already have the project on your computer, clone it. If you do, open a terminal inside the project folder.
2. Run: `git fetch origin`
3. Run: `git checkout feature/frontend-pages`
4. This branch already has your Hero, LeadersStrip, and other homepage components on it — you're building on top of your own work, not starting fresh.

## Step 2: Set up your local environment

1. Ask Engineering (Ayobami) for a `.env` file with the backend URL and the shared login secret.
2. Run `npm install` inside the `frontend` folder.
3. Run `npm run dev` to start the app on your computer — it should open at `http://localhost:3000`.
4. If `npm run dev` or `npm run lint` give a "command not found" type error, just run `npm install` again first — this is a known, harmless local setup hiccup, not a real problem.

## Step 3: What to build, in order

Build these one at a time, in this order, so each one unlocks the next:

1. **Login page** — a simple sign-in form using NextAuth.
2. **Upload form** — a file picker plus a few text fields (contributor name, source, LGA, description, rights status, related project ID). See the main PRD tab for the exact fields and how submitting should work.
3. **Admin review page** — only visible after logging in. Shows a list of pending uploads with Approve/Reject buttons.
4. **The four content pages** (Timeline, Explore Ekiti, My Ekiti Story, Ekiti 2056) — build these with placeholder/sample content for now, since the real backend data for them isn't ready yet.
5. **Ask Ekiti page** — just build the empty shell (a text box and an empty response area) — don't connect it to anything real yet.

## Step 4: How to save and submit your work

1. Save your changes often as you go: `git add .` then `git commit -m "describe what you did"`.
2. Push your work: `git push`.
3. **Important: never push directly to `main`.** Always stay on `feature/frontend-pages`.
4. When a page or feature is ready for review, open a Pull Request on GitHub comparing `feature/frontend-pages` to `main`, and ask Engineering or Member 1 to review it.

## Step 5: If you get stuck

- Something in the backend doesn't match what's described here — ask Engineering, don't guess.
- A design detail isn't covered — check the main PRD tab first, then ask.
- A local setup error you can't figure out — send the exact error message, don't just say "it's not working."
