# Music Research V2.6 — coverage-aware chart repair (2026-11-15)

## Changes
- Keeps the V2.5 dark design and all 11 research screens and filter/export features.
- Removes the V2.5 strict all-source overlap gate, which artificially hid an otherwise valid source contribution.
- In combined normalized charts, each bucket averages only sources that have observations in that bucket; a hatched pale-amber band denotes fewer reporting sources than selected. The hover tooltip displays the ratio of contributing sources.
- In source-split views, each source ends where its own observations end. Real missing source dates are not interpolated or imputed.
- A chart absence is not evidence of zero listening. A missing reporting period is null, never an observed zero. Within a measured top-N chart, zero chart share means no chart entry, not zero total streams.
- Keeps the original full data packages separate. The APP ZIP omits redundant V2 raw observation CSV and duplicate weekly runtime JSON files; its self-contained embedded datasets continue to power all screens, exports and drilldowns.

## Important caveat
The average of available sources may change composition from week to week. Hatched regions indicate such changes, and should not be used for rigorous longitudinal pooled inference without restricting to a common source set. The weekly source-split view is the defensible default for direct comparison.

## Data provenance
This is an application-only change on the existing processed V2.1 data. It does not update Google Drive sources. Suspect pre-war YouTube repeated snapshots remain excluded by default. Spotify original coverage gaps remain.
