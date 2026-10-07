# Progress (branch `survey`)

Last updated 2026-10-07 by cloud worker A (rules 2026-10-07; batches A1-).

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
| A1 | 126968 - 171038 | 126968, 127101, 127691, 128249, 128250, 128418, 132298, 146391, 156699, 171038 | 170557, 170842; 128126 duplicate on reading of 127691 |
| A2 | 177631 - 201007 | 183416, 186598, 188499, 188507, 192353, 193609, 194224, 200131, 200625 | 177631, 187874, 191622, 201007 |
| A3 | 205469 - 345036 | 207157, 224799, 262467, 271523, 288889, 301620, 318486, 333269, 345036 | 205469, 255502, 266142, 299799 |
| A4 | 345289 - 361689 | 345289, 356844, 359806, 360536, 361360, 361508, 361521, 361532, 361554, 361565, 361567, 361675, 361689 | - |
| A5 | 361718 - 361847 | 361718, 361725, 361783, 361785, 361786, 361794, 361802, 361827, 361834, 361839, 361844, 361847 | 361719 |
| A6 | 361880 - 362092 | 361880, 361969, 361974, 361977, 361996, 362000, 362004, 362031, 362055, 362059, 362060, 362089, 362092 | - |
| A7 | 362103 - 362418 | 362103, 362163, 362167, 362168, 362172, 362178, 362210, 362214, 362223, 362256, 362327, 362403, 362418 | - |
| A8 | 362427 - 362664 | 362427, 362430, 362443, 362457, 362497, 362499, 362542, 362572, 362637, 362638, 362649, 362654, 362664 | - |

## Next

1. Continue the queue: `overall == PORT_CANDIDATE` in `screening.csv`, ascending `fmz_id`,
   skipping ids already in `review_decisions.csv`. **Next id: 362667** (worker A works upward
   from 126968 on branch `survey`; worker B ports ids >= 439378 on `survey-b`, then works
   down from 439377; A stops when its next id is one B has done).
   Worker A's log with resume points: `reports/cloud_porting_A_LOG_2026-10-07.md`.
2. Before porting any file, check `near_duplicate_groups.csv` (and `possible_duplicates.csv`)
   for its id. Rule 7 (2026-10-07): near-duplicates are still ported, with their group id in
   PORT_NOTES.md; only an exact duplicate (same logic and defaults) is set aside, recorded in
   `port_manifest.DUPLICATE_ON_READING` -> `review_decisions.csv` as `DUPLICATE_ON_READING`.
3. After each batch: `python3 survey_tools/make_port_files.py && python3 survey_tools/check_ports.py
   && python3 survey_tools/summarize.py`, update this file, commit, push.

## Reverse in one bar; flat-first variant pending decision

The contract prefers flat before reverse (swap is booked on the first flat bar). These batch-1
ports reverse in one bar and are deliberately left unchanged until the project decides whether to
add flat-first variants (each would be a separate trial):

| Port | FAMILY | Reversal |
|---|---|---|
| `ports/11604_rsi-now-sb-ok/` | rsi_oscillator | buy/sell RSI zone crosses, always in market |
| `ports/55839_strategy/` | ichimoku | buy/sell on the Tenkan+Kijun double cross |
| `ports/119038_paul-the-gambler-l-vy-gold-edition/` | stop_and_reverse_bracket | opposite entry on a stop-out |

## Contract fix pass 2026-10-03

`FAMILY` added to all 6 ports (proposed, user to confirm; reasons in each PORT_NOTES.md);
`check_ports.py` now requires `FAMILY` and rejects any occurrence of `KNOWN_ANSWER_TEST`;
SURVEY_README.md: stops-Series timing corrected, flat-before-reverse and FTMO time-exit rules added.

## Open questions for the project (do not block porting)

1. **Volume**: 548 candidates use volume. Does `raw_1m_df` carry volume, and is it meaningful
   for the project's CFDs (broker tick volume)? Until answered they stay `HELD_NEEDS_VOLUME`.
2. ~~**Stops as Series**~~ ANSWERED 2026-10-03: the engine passes stop Series to vbt unlagged and
   vbt reads them on the fill bar, so per-bar stops must be built from the previous bar
   (`(k*atr/close).shift(1)`). SURVEY_README.md corrected; no batch-1 port returns a stop Series.
3. ~~**Criterion 4 boundary**~~ ANSWERED 2026-10-07 by rules 2-4 in SURVEY_README.md. Was: fixed stop/target exits are ported via `stops()` *and* stored;
   trailing stops that `stops()` cannot express are stored only (or ported as a close-based
   signal exit when they are the strategy's only exit). Confirm this split.
4. ~~**Undeclared bar size**~~ ANSWERED 2026-10-07 (rule 1): `FREQ = "bar_size_pending"` + mark;
   applied to 11604, 42283, 42451, 119038 (logic unchanged).

## How to resume in a new session

```
git fetch origin survey && git checkout survey
python3 survey_tools/screen.py          # deterministic; re-creates screening.csv etc.
python3 survey_tools/check_ports.py     # static contract check of all ports (no execution)
```
Add each new port as `ports/<fmz_id>_<slug>/module.py` + `PORT_NOTES.md` (slug from
`screening.csv`), add its sizing line ranges to `survey_tools/port_manifest.py` (and any
rejections to `REJECTED_ON_READING`), then run step 3 above.
