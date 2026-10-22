# #439260 基于SMA和ATR的趋势追踪策略SMA-and-ATR-Based-Trend-Tracking-Strategy -> `fmz_439260_sma100_three_bar_pullback`

- FMZ source id: 439260 (lineage).
- Source: https://www.fmz.com/strategy/439260 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 16:04:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet stop pending |
| 2 | PASS | SMA side and close sequences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [100, 200] x `run` [3, 2]: **4 trials**.

## Ambiguities resolved

- Ratchet ATR stop pending (entries only). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`trailing_stop_pending`
