# Music Research V2.4 — navigation and live update repair

This release retains the V2.3 dark interface and data (including 7,960 suspect YouTube observations excluded from calculations by default).

Changes:
- Dedicated, explicit default analysis for Songs, Creators, Overview and Breakdowns when clicking the main navigation.
- A visible list of the current top ten songs/creators above the time chart; complete searchable selection and composition remains underneath.
- Reset contextual drilldown filters when returning to analysis tabs, without deleting ordinary filters.
- Update the ranking, graph, selection panel, totals and summary together after filtering and changing language.
- Debounce the global search field (250ms) to prevent a full graph rebuild per keystroke.
- All existing tabs and export options preserved.

Known research caveats: YouTube pre-October 2023 duplicated snapshots remain excluded; no missing values converted to zero; Spotify daily and YouTube weekly are different observation frequencies.
