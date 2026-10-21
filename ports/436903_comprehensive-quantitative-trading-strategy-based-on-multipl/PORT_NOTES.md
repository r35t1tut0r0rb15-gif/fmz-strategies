# #436903 Comprehensive Quantitative Trading Strategy Based on Multiple Indicators -> `fmz_436903_supertrend_qqe_tia_long_state`

- FMZ source id: 436903 (lineage).
- Source: https://www.fmz.com/strategy/436903 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 17:46:45). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR SuperTrend, RSI band and EMA comparison |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG436903. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_mult` [3.9, 2.5] x `tia_len` [52, 26]: **4 trials**; ST ATR 9, QQE 6 / 5 and the 50-bar band fixed.

## Ambiguities resolved

- close[2] SuperTrend as written; three-valued QQE test; both-sides branch off and not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
