# #436772 Bollinger Bands Heiken Ashi Short term Trading Strategy -> `fmz_436772_heikin_ashi_bollinger_width`

- FMZ source id: 436772 (lineage).
- Source: https://www.fmz.com/strategy/436772 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 15:52:08). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit width threshold -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`consecutive` [1, 2] x `vol_frac` [0.0000067, 0.5]: **4 trials**; Bollinger 4 / 20 fixed.

## Ambiguities resolved

- Price-unit width threshold -> fraction of the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
