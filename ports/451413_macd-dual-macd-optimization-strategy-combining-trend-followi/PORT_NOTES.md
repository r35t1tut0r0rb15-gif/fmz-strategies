# #451413 趋势跟踪与动量交易相结合的双重MACD优化策略-Dual-MACD-Optimization-Strategy-Combining-Trend-Following-and-Momentum-Trading -> `fmz_451413_macd_signal_cross_sma50_long_bracket_short_one_bar`

- FMZ source id: 451413 (lineage).
- Source: https://www.fmz.com/strategy/451413 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 17:35:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close |
| 2 | PASS | MACD signal crossings with an SMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 12] x `slow` [21, 26] x `sma_len` [50, 100]: **8 trials**; the signal length and the bracket fractions fixed.

## Ambiguities resolved

- Long bracket from the fill bar; the short closes after its first bar (wrong-side levels). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`coarse_bar_stop`
