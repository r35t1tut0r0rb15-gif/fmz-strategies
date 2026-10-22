# #439262 基于伦敦SMA交叉的ETH反转交易策略London-SMA-Cross-ETH-Reversal-Trading-Strategy -> `fmz_439262_close_sma50_cross_daily`

- FMZ source id: 439262 (lineage).
- Source: https://www.fmz.com/strategy/439262 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 16:08:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [50, 20, 100]: **3 trials**.

## Ambiguities resolved

- Session filter unused, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
