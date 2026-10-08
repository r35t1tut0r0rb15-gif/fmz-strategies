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
| A9 | 362667 - 363579 | 362667, 362671, 362842, 362868, 362870, 362887, 362898, 363001, 363002, 363562, 363579 | 363557, 363572 |
| A10 | 363582 - 363847 | 363582, 363588, 363590, 363749, 363766, 363793, 363797, 363803, 363807, 363824, 363825, 363829, 363847 | - |
| A11 | 363848 - 365075 | 363848, 363980, 363997, 364001, 364037, 364518, 364527, 364535, 364536, 364540, 365028, 365059, 365075 | - |
| A12 | 365078 - 365389 | 365078, 365080, 365127, 365128, 365283, 365314, 365315, 365320, 365345, 365359, 365373, 365381 | 365389 |
| A13 | 365419 - 365727 | 365419, 365600, 365642, 365668, 365671, 365691, 365695, 365706, 365711, 365713, 365719, 365722, 365727 | - |
| A14 | 365858 - 366430 | 365858, 365859, 365892, 365898, 365905, 365907, 366385, 366388, 366389, 366391, 366404, 366407, 366430 | - |
| A15 | 366641 - 367572 | 366641, 366930, 366936, 366941, 366942, 366943, 366946, 366947, 366948, 366966, 367476, 367565, 367572 | - |
| A16 | 367643 - 370711 | 367643, 368715, 368736, 368738, 368749, 368777, 369392, 370653, 370655, 370711 | 368717, 368734, 369999 |
| A17 | 370728 - 380396 | 376314, 379757, 379760, 380007, 380219, 380245, 380251, 380277, 380291, 380331, 380369, 380396 | 370728 |
| A18 | 380446 - 416875 | 380525, 385745, 391341, 395962, 396182, 400134, 402455, 410112 | 380446, 380530, 392636, 395966, 416875 |
| A19 | 422794 - 426259 | 425773, 425796, 425797, 425882, 426136, 426137, 426141, 426142, 426145, 426249, 426259 | 422794, 425798 |
| A20 | 426261 - 426360 | 426262, 426298, 426300, 426322, 426335, 426338, 426339, 426340, 426359, 426360 | 426261, 426302, 426334 |
| A21 | 426361 - 426478 | 426363, 426367, 426368, 426376, 426377, 426391, 426460, 426477 | 426361, 426364, 426455, 426461, 426478 |
| A22 | 426482 - 426516 | 426482, 426483, 426486, 426487, 426489, 426498, 426500, 426502, 426506, 426510, 426511, 426516 | 426509 |
| A23 | 426521 - 426604 | 426521, 426557, 426561, 426571, 426579, 426581, 426587, 426593, 426598, 426604 | 426556, 426570, 426588 |
| A24 | 426610 - 426779 | 426612, 426613, 426616, 426618, 426619, 426625, 426626, 426774, 426776, 426778, 426779 | 426610, 426621 |
| A25 | 426780 - 426811 | 426780, 426783, 426786, 426794, 426797, 426799, 426801, 426806, 426807, 426808, 426810 | 426781, 426811 |
| A26 | 426812 - 426847 | 426812, 426816, 426824, 426829, 426834, 426836, 426838, 426842, 426843, 426844, 426847 | 426825, 426832 |
| A27 | 426848 - 426886 (+ re-read 426461, 426509, 426588) | 426848, 426852, 426854, 426855, 426856, 426879, 426883, 426884, 426885, 426886, 426461, 426509, 426588 | 426849, 426850, 426882 |
| A28 | 426888 - 426925 | 426888, 426889, 426891, 426894, 426895, 426901, 426902, 426904, 426905, 426906, 426908, 426923, 426925 | - |

## Next

1. Continue the queue: `overall == PORT_CANDIDATE` in `screening.csv`, ascending `fmz_id`,
   skipping ids already in `review_decisions.csv`. **Next id: 426928** (worker A works upward
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
