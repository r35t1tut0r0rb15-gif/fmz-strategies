# #437022 Dynamic Take Profit Following Trend Strategy -> `fmz_437022_rsi200_pullback_bhd_exits`

- FMZ source id: 437022 (lineage).
- Source: https://www.fmz.com/strategy/437022 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 16:06:54). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits tested on closes |
| 2 | PASS | Volatility-unit exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash quantity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [200, 100] x `sl_units` [2.0, 1.0]: **4 trials**; RSI level 51, two falling closes, TP 1 unit and the 50 / 100 unit lengths fixed.

## Ambiguities resolved

- Close-tested exits from the fill price; window and last-bar close dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
