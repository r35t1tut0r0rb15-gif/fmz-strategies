# #435106 MACD Strategy Two Way Exit Trading -> `fmz_435106_macd_far_side_swing_bracket`

- FMZ source id: 435106 (lineage).
- Source: https://www.fmz.com/strategy/435106 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 12:44:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | MACD crosses, an average filter and swing-based exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot sizes and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 1.0] x `swing` [7, 14]: **4 trials**; EMA 200 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Flat tracked through the bracket. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
