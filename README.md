# Music Research APP 2.6 — self-contained dark research dashboard

Open `index.html` after extracting the ZIP. Data are embedded in the HTML; no manual installation or V2 DATA package is required. The application remains portable to static hosting.

The 11 research screens, charts, creators/songs, source comparisons, filtering, zoom, exports, events, identity links, and Hebrew/English interface are retained from V2.5.

## Data coverage
Normalized merged series use only sources actually observed in each period. The amber hatched area identifies periods where fewer than all selected sources were available; hovering shows contributing source count. For research requiring a fixed source panel, use the secondary `Source` split. Real source gaps and the repeated suspect YouTube early-2023 snapshots remain excluded rather than imputed. Lack of a chart entry is not lack of listening.

## Size
The APP zip excludes redundant V2 full observations CSVs, separate weekly JSON copies and the original XLSX archives. Core data for all visuals and raw-row exports remain embedded. Three useful compact reference CSV catalogs are included. Original Google Sheets are linked from the data screen, rather than duplicated. The full DATA V2.1 package remains a separate research archival release.

## Testing
Chromium-based DOM tests confirmed load of all 222,550 underlying records; source coverage calculations; all 11 research screens; song source comparisons; zoom; language switch and reset. `file://` direct navigation is blocked by the test environment, so double-click/open-file behavior could not be independently checked there.
