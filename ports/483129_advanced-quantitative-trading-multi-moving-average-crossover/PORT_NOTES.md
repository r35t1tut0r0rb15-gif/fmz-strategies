# #483129 Advanced Quantitative Trading Multi Moving Average Crossover System with Volume Filter Strategy -> `fmz_483129_ema9_21_cross_sma50_volume_1pct_stop_reversal`

- FMZ source id: 483129 (lineage).
- Source: https://www.fmz.com/strategy/483129 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:50:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 1 % stop from the fill |
| 2 | PASS | EMA crossings with an SMA 50 trend filter on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.01, 0.02] x `tp` [4.0, 0.05]: **4 trials**; EMA 9 / 21, SMA 50, volume x 1.5.

## Ambiguities resolved

- Bracket from the fill (source: from the bar after); the 400 % target never fills. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
