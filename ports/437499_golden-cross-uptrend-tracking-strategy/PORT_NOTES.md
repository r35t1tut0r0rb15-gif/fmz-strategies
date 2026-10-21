# #437499 Golden Cross Uptrend Tracking Strategy -> `fmz_437499_golden_death_cross`

- FMZ source id: 437499 (lineage).
- Source: https://www.fmz.com/strategy/437499 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 11:46:44). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- Shorts as coded (the comment says long only). REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
