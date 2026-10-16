# #430036 Trend Reversal Volatility Combination Strategy -> `fmz_430036_combo_123_stat_volatility`

- FMZ source id: 430036 (lineage).
- Source: https://www.fmz.com/strategy/430036 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-24 14:23:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a log-range volatility of the window. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_sv` [30, 60] x `top_band` [0.005, 0.01]: **4 trials**; low band 0.0016 and the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
