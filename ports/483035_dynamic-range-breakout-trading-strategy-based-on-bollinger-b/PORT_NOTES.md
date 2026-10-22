# #483035 Dynamic Range Breakout Trading Strategy Based on Bollinger Bands and RSI -> `fmz_483035_bb20_2_lower_reentry_rsi45_upper_exit_long`

- FMZ source id: 483035 (lineage).
- Source: https://www.fmz.com/strategy/483035 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:17:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band re-entries with RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 1.5]: **4 trials**; RSI 14, buy under 45, exit over 70.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
