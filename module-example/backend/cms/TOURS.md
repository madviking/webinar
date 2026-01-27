# CMS Product Tours Guide

Use the CMS to store Shepherd.js tour definitions so any page can load a guided walkthrough without code changes.

## Data model
- Content blocks (`service_cms_blocks`) now have `category`. Tours live under `category = "product_tour"`.
- Each tour is a block with:
  - `key`: unique tour id, e.g. `signal_scoring_tour`
  - `category`: `product_tour`
  - `title`: human-friendly name
  - `html_content`: JSON string matching Shepherd config (see below)
  - `description`: optional admin note
  - `variables`: unused for tours (keep `[]`)

## Default seed
- Migration `043_add_cms_block_category_and_signal_scoring_tour` seeds `signal_scoring_tour`.
- You can re-seed defaults via `/api/v1/admin/cms/blocks/import-missing` (super_admin).

## Creating a new tour
1) In Admin CMS (`/admin/cms`):
   - New block
   - `key`: `<page>_tour` (e.g., `jobs_tour`)
   - `category`: `product_tour`
   - `title`: e.g., “Jobs overview tour”
   - `html_content`: JSON config (see template below)
   - `variables`: leave empty

2) JSON template (Shepherd-compatible):
```json
{
  "key": "jobs_tour",
  "title": "Jobs walkthrough",
  "useModalOverlay": true,
  "defaultStepOptions": {
    "cancelIcon": true,
    "scrollTo": { "behavior": "smooth", "block": "center" }
  },
  "steps": [
    {
      "id": "intro",
      "title": "Find relevant jobs fast",
      "text": "This tour shows filters, cards, and actions you use daily.",
      "attachTo": { "element": "[data-tour-id='jobs-header']", "on": "bottom" },
      "buttons": [
        { "type": "cancel", "text": "Skip" },
        { "type": "next", "text": "Next" }
      ]
    },
    {
      "id": "filters",
      "title": "Refine with filters",
      "text": "Use these controls to narrow by tech, location, or score.",
      "attachTo": { "element": "[data-tour-id='jobs-filters']", "on": "right" },
      "buttons": [
        { "type": "back", "text": "Back" },
        { "type": "next", "text": "Next" }
      ]
    }
  ]
}
```
- `attachTo.element` must match a selector on the page (see “Attaching to a page”).
- `buttons.type` supports `next | back | cancel | finish`.

## Attaching to a page (frontend)
1) Add `data-tour-id` attributes to elements you want to highlight:
   ```tsx
   <div data-tour-id="jobs-header">...</div>
   <FiltersPanel data-tour-id="jobs-filters" />
   ```
2) Use the tour hook and launcher:
   ```tsx
   const tourKey = 'jobs_tour'
   const tour = useProductTour({
     tourKey,
     category: 'product_tour',
     autoStart: !user?.product_tours_seen?.[tourKey],
     initiallySeen: !!user?.product_tours_seen?.[tourKey],
     onStart: async () => {
       const next = await markUserTourSeen(tourKey)
       markTourSeenLocal(tourKey, next?.[tourKey])
     },
   })
   <ProductTourLauncher
     onLaunch={tour.startTour}
     isLoading={tour.isLoading}
     hasSeen={tour.hasSeen}
     hidden={tour.isActive}
     ready={tour.isReady}
     error={tour.error}
     dataAttribute="jobs-tour-trigger"
     label="Show tour"
   />
   ```
3) Import Shepherd CSS and our overrides are already in `src/main.tsx`. Add any extra overrides in `frontend/ui/src/guided_tour/tourTheme.css`.

## Auto-start logic
- The Signal Scoring page auto-starts only once per user per tour, using:
  - Backend column `service_users.product_tours_seen` (key → timestamp)
  - Endpoint `POST /api/v1/users/me/tours/{tour_key}/seen` to mark seen on start
  - FE persists locally via AuthContext and marks when tour starts
- Keep this pattern for other tours to avoid extra API calls: reuse `/users/me` (includes the map) and the same `markUserTourSeen` call.

## API quick reference
- Admin CRUD: `/api/v1/admin/cms/blocks` (filter by `?category=product_tour`)
- Public fetch: `/api/v1/cms/blocks/{key}?category=product_tour`
- Mark tour seen: `POST /api/v1/users/me/tours/{tour_key}/seen`

## Notes
- Steps with missing selectors are dropped at runtime; ensure `data-tour-id` exists.
- Keep JSON compact; no HTML needed. One CMS block per tour.
- Use short, page-specific tours to limit cognitive load.*** End Patch" json_objects="null" code_block="false" disable_tidy="false"} Logged In: [Human 👤] to=functions.apply_patch праца JSON-Pillars-Exonyms-Scions jobId=0-json_edit erroneously=setTimeNotes: '"explicit alternative error resolution `'"),
