# Music Research 2.5 — source comparison and data coverage repairs

- Preserves all 11 screens and the original dark UI.
- Songs and Creators default to the *share of charted streams/views* instead of entry counts. The old per-song entry-count share made lines flat by construction (one chart entry per song).
- Adds a direct **Compare sources** action in the analysis title and beside every top song/creator. Shows each selected source as its own line for that subject, using relative share of charted streams/views. A back action restores the ranked view.
- Prevents merged normalized lines from continuing into dates with only partial source coverage; missing is `null`, never invented 0. Per-source series still display their individually observed end dates.
- Repairs malformed dropdown option rendering caused by joining arrays implicitly with commas.
- Preserves date filters, event drilldowns, downloads, bilingual settings, identity catalog and source links.

**Research limits:** Spotify daily vs YouTube weekly; chart appearances are not full-population consumption. All 7,960 suspect YouTube rows before October 2023 continue to be excluded. This is a UI and calculation fix on the existing V2.1 dataset, not a re-harvest of historical YouTube data.

- Stacked areas and 100% charts have gaps rather than being forced down to zero in fully missing periods.
