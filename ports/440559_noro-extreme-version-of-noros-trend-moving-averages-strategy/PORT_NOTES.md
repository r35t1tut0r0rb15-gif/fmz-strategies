# #440559 极端的Noro趋势均线策略Extreme-version-of-Noros-Trend-Moving-Averages-Strategy -> `fmz_440559_noro_trend_channel_extreme`

- FMZ source id: 440559 (lineage).
- Source: https://www.fmz.com/strategy/440559 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-31 17:00:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-channel centres and bar colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427506. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slowlen` [21, 50] x `fastlen` [5, 10]: **4 trials**; bars 2 fixed.

## Ambiguities resolved

- Stops off place nothing; short wins a same-bar tie. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
