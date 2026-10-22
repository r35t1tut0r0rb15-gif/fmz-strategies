# #443241 RSI与平滑RSI策略多头分型RSI-and-smoothed-RSI-bullish-divergence-strategy -> `fmz_443241_rsi_hull_bull_divergence_pct_bracket_long`

- FMZ source id: 443241 (lineage).
- Source: https://www.fmz.com/strategy/443241 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-01 12:11:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | RSI divergence with a smoothed RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_curve` [14, 7] x `div_lookback` [25, 50]: **4 trials**; the levels and the bracket fixed.

## Ambiguities resolved

- Percent-over-tick bracket as fixed fractions; lowestbars as the most recent low. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
