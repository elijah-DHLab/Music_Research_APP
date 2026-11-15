# Music Research — V2 with preserved legacy interface

This package preserves the original 10 research screens, adds the V2 performance catalog, and includes a self-contained V2 data snapshot.

## Starting

Open `index.html` after extraction (file:// has JS data fallback) or publish the contents of `site/` on a static HTTP host. No external data connection is required. Chromium is recommended.

## Data

`index.html` embeds the compact adapter from V2 observations, keyed by `performance_id`, so it can open without a server. Full V2 tables and weekly evidence are under `data/v2/`, with `data/v2/runtime/manifest.json`, `data/v2/docs/INTEGRATION_CONTRACT_HE.md`. This V2 snapshot is the previously validated data snapshot, not the later unprocessed Google Drive files.

## Research rules

Records flagged suspect_repeated_snapshot are preserved but excluded by default. A dedicated switch permits inspection only; missing weeks are not zeros. No sums of Spotify streams and YouTube views are scientifically comparable. Identities are provisional until reviewed. The old chart UI uses performance IDs as its grouping key; metadata inherited from earlier catalog matches should be reviewed.

## Features retained

Ten original screens: Overview, Songs, Artists, Breakdown, Period comparison, Research questions, Events, Raw data, API, Help. Also: drag-to-zoom, click-to-drilldown, source comparisons, series picker, exports, language switch, color palette, chart types and annotations. New 11th screen: V2 performance catalog.
