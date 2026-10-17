# #432778 Super Guppy Moving Average Trading Strategy -> `fmz_432778_super_guppy_slow_ribbon`

- FMZ source id: 432778 (lineage).
- Source: https://www.fmz.com/strategy/432778 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 14:05:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA ribbon order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`step` [3, 2] x `first` [24, 12]: **4 trials**; fifteen slow EMAs from `first` in steps of `step` (24 / 3 as written).

## Ambiguities resolved

- Early-signal block only. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
