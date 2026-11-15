# Music Research V2.3 — visual refinement

This release preserves V2.2 data and all application screens. Only display logic and context help changed.

- Every concurrently visible chart series has a distinct color. Language/source category colors remain preferentially fixed; in case of collisions a deterministic secondary tone is assigned. Colors of colliding dynamic series can differ when the set of displayed series changes.
- Small accessible information markers beside filter names and chart grouping/split controls explain the provenance and methodological limitations of country, city, genre, artist type, language, song, rank-related categories and more.
- In particular `country` represents the original `birth_or_origin_country` field: person's birth country OR group's origin/formation country; it must not be confused with citizenship or streaming location.
- Help works in Hebrew and English, on hover or keyboard focus.

Validation: syntax check via Node and Chromium Playwright `set_content` smoke test (artist/song chart colors, country tooltip, language toggle). Direct file:// loading blocked by environment policy, not independently tested.
