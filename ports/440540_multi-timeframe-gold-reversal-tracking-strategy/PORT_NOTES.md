# #440540 Multi Timeframe Gold Reversal Tracking Strategy -> `fmz_440540_gold_swing_many_signals_last_wins`

- FMZ source id: 440540 (lineage).
- Source: https://www.fmz.com/strategy/440540 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 15:01:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price levels and step -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_level` [1.5, 3.0] x `scalp_frac` [2.4e-6, 0.002]: **4 trials**; level fractions fixed.

## Ambiguities resolved

- Price levels as fractions (scalp entries dominate on BTC); last entry wins. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
