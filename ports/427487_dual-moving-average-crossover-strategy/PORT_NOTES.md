# #427487 Dual Moving Average Crossover Strategy -> `fmz_427487_sma_cross_min_gain_long`

- FMZ source id: 427487 (lineage).
- Source: https://www.fmz.com/strategy/427487 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 16:40:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; gain test on the close. |
| 2 | PASS | MA lengths, percent of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented-out sizing line stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `slow` [28, 56] x `min_gain_pct` [0.6, 1.5]: **8 trials**; defaults 14 / 28 / 0.6 (the source's).

## Ambiguities resolved

- strategy() is commented out: pyramiding 0, so the averaging add never fills; average = entry fill.
- Long only. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
