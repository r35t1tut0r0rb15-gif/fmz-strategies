# #434458 双均线ADX择时策略Dual-Moving-Average-ADX-Timing-Strategy -> `fmz_434458_combo_2_20_ema_adxr`

- FMZ source id: 434458 (lineage).
- Source: https://www.fmz.com/strategy/434458 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-06 15:48:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An average side and ADXR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `signal2` [45, 30]: **4 trials**; ADX 14, ADXR 14 and signal 1 = 13 fixed.

## Ambiguities resolved

- Start date dropped. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
