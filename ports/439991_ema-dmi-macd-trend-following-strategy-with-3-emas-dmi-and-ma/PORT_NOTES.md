# #439991 三EMA配合DMI和MACD的趋势跟踪策略Trend-Following-Strategy-with-3-EMAs-DMI-and-MACD -> `fmz_439991_ema34_dmi17_adx_state`

- FMZ source id: 439991 (lineage).
- Source: https://www.fmz.com/strategy/439991 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:48:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side and DMI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [14, 21] x `di_level` [17, 25]: **4 trials**; EMA 34 fixed.

## Ambiguities resolved

- Both tests on one bar favour the short. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
