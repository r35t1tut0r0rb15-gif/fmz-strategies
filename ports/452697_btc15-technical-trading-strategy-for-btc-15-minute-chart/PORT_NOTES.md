# #452697 基于BTC15分钟图表的技术交易策略-Technical-Trading-Strategy-for-BTC-15-minute-Chart -> `fmz_452697_wavetrend_divergence_atr_stop_long_only`

- FMZ source id: 452697 (lineage).
- Source: https://www.fmz.com/strategy/452697 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 11:15:29). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal bar as a fraction of the fill |
| 2 | PASS | WaveTrend / price divergences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 1 % / stop distance x 2, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG452697. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n1` [10, 9] x `stop_atr` [1.5, 2.5]: **4 trials**; n2 21, ATR 14.

## Ambiguities resolved

- Stop fixed at the entry signal (re-sent later in Pine). Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
