# Progress (branch `survey`)

Last updated 2026-09-29 by session 5E-cloud.

## Done

- **Screen (criteria 1, 2, 3, 6)**: all 5,806 corpus files screened statically -> `screening.csv`,
  `duplicates.csv`, `possible_duplicates.csv`. Counts: `SURVEY_SUMMARY.md`.
- **Criterion 3 store**: 253 crypto-exchange-only files copied to `flagged/<id>_<slug>/` with
  `REASON.md`.
- **Batch 1** (queue positions 1-13, FMZ ids 179 to 119038): 6 ported, 7 rejected on reading
  (`review_decisions.csv`).

| Batch | FMZ ids read | Ported | Rejected on reading |
|---|---|---|---|
| 1 | 179 - 119038 | 11604, 42283, 42451, 55839, 103070, 119038 | 179, 21104, 21369, 21370, 23531, 23874, 62163 |

## Next

1. Continue the queue: `overall == PORT_CANDIDATE` in `screening.csv`, ascending `fmz_id`,
   skipping ids already in `review_decisions.csv`. **Next id: 126968** (MyLanguage turtle).
   About 40 FMZ-API bots (JavaScript/Python/MyLanguage) remain before the PineScript block,
   which starts at 356844.
2. Before porting any file, check `possible_duplicates.csv` for its id. If the partner's logic
   is the same, collapse it: record it in `review_decisions.csv` as `DUPLICATE_ON_READING` of the
   representative (the one ported or to be ported) and add it to that port's notes.
3. After each batch: `python3 survey_tools/make_port_files.py && python3 survey_tools/check_ports.py
   && python3 survey_tools/summarize.py`, update this file, commit, push.

## Open questions for the project (do not block porting)

1. **Volume**: 548 candidates use volume. Does `raw_1m_df` carry volume, and is it meaningful
   for the project's CFDs (broker tick volume)? Until answered they stay `HELD_NEEDS_VOLUME`.
2. **Stops as Series**: when `stops()` returns a per-bar Series (ATR-scaled), does the engine
   read it on the signal row or on the fill row? The ports assume the engine lags it like signals.
3. **Criterion 4 boundary**: fixed stop/target exits are ported via `stops()` *and* stored;
   trailing stops that `stops()` cannot express are stored only (or ported as a close-based
   signal exit when they are the strategy's only exit). Confirm this split.
4. **Undeclared bar size**: ports whose source gives no period use `FREQ = "1h"`. Confirm, or name
   a different default.

## How to resume in a new session

```
git fetch origin survey && git checkout survey
python3 survey_tools/screen.py          # deterministic; re-creates screening.csv etc.
python3 survey_tools/check_ports.py     # static contract check of all ports (no execution)
```
Add each new port as `ports/<fmz_id>_<slug>/module.py` + `PORT_NOTES.md` (slug from
`screening.csv`), add its sizing line ranges to `survey_tools/port_manifest.py` (and any
rejections to `REJECTED_ON_READING`), then run step 3 above.
