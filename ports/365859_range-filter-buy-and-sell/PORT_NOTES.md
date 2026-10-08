# #365859 Range Filter Buy and Sell 5min [Strategy] -> `fmz_365859_range_filter_flip`

- Source: https://www.fmz.com/strategy/365859 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-26 12:25:38). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365859` (Jaccard >= 0.80) with #368724 (DUPLICATE), #427523 (DUPLICATE); best Jaccard 0.985 with #427523. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [25, 50, 100] x `mult` [2.0, 3.0, 4.0] = **9 trials**.

## Ambiguities resolved

- window() returns true; optional stop/take-profit default off; HA candles off.
- Same mechanics as #363562 with other defaults.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
