# #483793 Enhanced Doji Candlestick Trend Reversal Quantitative Trading Strategy -> `fmz_483793_doji_confirm_tick_stop_2r_doji_close_reversal`

- FMZ source id: 483793 (lineage).
- Source: https://www.fmz.com/strategy/483793 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:33:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C260). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill |
| 2 | ADAPT | 5-tick stop read as a fraction at ETH 3000 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [1.667e-05, 0.005] x `risk_reward` [2.0, 3.0]: **4 trials**; doji threshold 0.3.

## Ambiguities resolved

- The 5-tick stop is read at ETH 3000. The doji closes are followed in a loop. REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
