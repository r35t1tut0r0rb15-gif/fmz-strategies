# #438058 双MA顺势突破策略Dual-MA-Trend-Breakout-Strategy -> `fmz_438058_noro_trend_mas_cryptobottom`

- FMZ source id: 438058 (lineage).
- Source: https://www.fmz.com/strategy/438058 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 16:43:38). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-channel centres, bar colours, a fast RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the unused stop percent stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427506. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slowlen` [21, 40] x `fastlen` [5, 10]: **4 trials**; bars 2, extreme on and stops off fixed.

## Ambiguities resolved

- Stops off: exits place no order; dn2 always 0. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
