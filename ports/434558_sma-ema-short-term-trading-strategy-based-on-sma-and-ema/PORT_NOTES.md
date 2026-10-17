# #434558 基于SMA和EMA指标的短线交易策略Short-term-Trading-Strategy-Based-on-SMA-and-EMA -> `fmz_434558_ema_sma_cross_close_exits`

- FMZ source id: 434558 (lineage).
- Source: https://www.fmz.com/strategy/434558 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 15:29:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-sized exits fixed at entry (approximation stated) |
| 2 | PASS | Average crosses and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [21, 10] x `tp_pct` [0.02, 0.04]: **4 trials**; SMA 20 and the 1 % stop fixed.

## Ambiguities resolved

- Close-sized exits fixed at the fill (trailing_stop_pending). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
