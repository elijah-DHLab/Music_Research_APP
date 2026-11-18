# Data dictionary — Version 2.0

CSV encoding: UTF-8 with BOM (Excel-friendly); commas as separators; blank fields mean unknown/unverified, **never numeric zero**. Dates follow ISO-8601 `YYYY-MM-DD`. All IDs are text; never cast numeric-looking identifiers to numbers.

**Primary observation**: `observations.observation_id` unique; `source_id` foreign key to sources; `source_item_id` foreign key to source_items; `performance_id` foreign key to performances. `chart_start_date` and `chart_end_date` express the **source reporting interval**, not necessarily a listening timestamp. `measure_value` holds streams or views; compare only within unit or normalize explicitly. `data_status=observed` indicates source row exists, not that all columns were nonmissing.

**Performance**: `performances.performance_id` primary key; `identity_status` records whether one source item, provisional exact credit-set link, or organization requiring review. `language_verified`/`genre_verified` intentionally blank and must not be inferred from title script/artist genre as authoritative facts.

**Platform item**: `source_items.source_item_id` primary key, e.g. `sp:spotify:track:...` and `yt:VIDEOID`. YouTube Tracks and Videos can both refer to the same video ID, but their *observations* remain distinct, because their charts/measurement frames differ. `identity_status=missing_platform_id_review` signals an unresolved platform identifier.

**Entities**: `entities.entity_id` primary key; `entity_kind∈{person,ensemble,organization_project,unknown}`. `source_entity_type` is the original spreadsheet classification even when inconsistent. `classification_status=needs_review` flags likely organizations/unknown items. This is not a definitive ontology of performers.

**Credits**: `source_item_credits` retains `credit_order` and `raw_credit_name`; sorting for exact matching does not erase order. `performance_entities` is a derived distinct relation; `role=platform_artist_credit` does *not* mean verified singer/performer.

**Works**: `works_provisional` one-to-one placeholders, `work_identity_status=placeholder_unverified_one_per_performance`. `performance_work_links` associates them. This **does not** constitute a verified works authority file; curator-approved work unifications must be implemented in V2 curation.

**Quality**: `quality_issues` contains source inconsistencies and entity-type warnings. `candidate_merges_review` lists selected uncertain title-sharing candidates; it is a review **queue**, not a comprehensive fuzzy matching score. `identity_decisions`, `entity_decisions`, `metadata_corrections` are intentionally empty templates (no decisions falsely implied).

**Coverage**: `coverage_observed` only contains measured source periods. `coverage_gaps` only lists gaps *between* first and last observed reporting periods. A period before the first observed chart or after the last one is also `no_data`, not zero, even though it is not separately materialized. An item absent from Top N in an observed period may have zero appearances **in that Top N**, but its plays/views in the full platform cannot be inferred to equal zero.

**Catalog**: `catalog_master_import` retains the imported master sheet identifiers and counts as source information, not as authoritative mapping to `performance_id`. Full two-tab source workbook is preserved in raw.

**Events**: `events.csv` replicates the event catalog from the previous site and marks it as requiring verification; no causal claims are encoded in the event annotations.

Important limit: the build script regenerates provisional identity groupings from the raw sources; it does **not yet** apply manual decision CSVs or import additional historical YouTube files automatically. Do not use it as a multi-user curation backend without extending this behavior.

Source-quality check: ten duplicate `(source_id, chart_end_date, rank)` combinations were found in YouTube charts. These are flagged in `quality_issues.csv` and intentionally preserved. The validation script checks the known count instead of silently dropping rows.

## Correction of 2026-11-18
- **One row per (source, date, track).** When two platform items (two Spotify URIs, or two YouTube videos) were merged into one track and both charted in the same period, they are stored as one row: `v` = sum of both, `r` and `pk` = the better of the two, `pr`/`dc` from the better-ranked item. Each merge is listed in `qa.merged_duplicate_rows` as `[source, date, performance_id, [ranks], [values]]`; `coverage.json` still counts them as source chart rows.
- **`data/unresolved_rows.csv`** lists every chart row the source left untitled: `in_app=yes` rows are in the data as an untitled item (counted in totals), `in_app=no` rows have neither title nor id and are not in the app.
- **`qa.merged_performances`** maps each removed `performance_id` to the one it was merged into.
