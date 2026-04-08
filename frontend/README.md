# TinyFish Frontend

React + TypeScript frontend for the TinyFish multi-agent scraping workflow.

## Run the frontend

From the `frontend` folder:

```bash
npm install
npm run dev
```

Vite will start the app locally (usually at `http://localhost:5173`).

## Backend connection

Make sure the backend API is running on:

`http://localhost:8000`

The frontend uses `VITE_API_BASE_URL` from `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## How to use the app

1. Enter a target URL.
2. Optionally enter a research goal.
3. Select one or more specialist types.
4. Click **Start Scrape**.
5. Watch live progress updates in the status cards/timeline.
6. View the final synthesized report and JSON result in the result viewer.
