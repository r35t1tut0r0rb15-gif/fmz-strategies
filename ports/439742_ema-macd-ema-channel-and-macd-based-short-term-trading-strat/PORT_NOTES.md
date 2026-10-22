# #439742 基于EMA通道和MACD的短线交易策略EMA-Channel-and-MACD-Based-Short-term-Trading-Strategy -> `fmz_439742_ema21_side_macd_scalp_entries`

- FMZ source id: 439742 (lineage).
- Source: https://www.fmz.com/strategy/439742 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 14:30:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket pending |
| 2 | PASS | EMA side, EMA crossings and the MACD histogram |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [21, 50] x `fast` [5, 9]: **4 trials**; MACD 18 / 34 / 12 fixed.

## Ambiguities resolved

- Per-bar bracket pending (entries only); last entry wins. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
