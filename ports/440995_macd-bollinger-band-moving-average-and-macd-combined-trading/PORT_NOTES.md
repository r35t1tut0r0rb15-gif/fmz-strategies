# #440995 基于布林带移动平均线和MACD的组合交易策略Bollinger-Band-Moving-Average-and-MACD-Combined-Trading-Strategy -> `fmz_440995_ema34_bb150_macd_once_per_side_bracket`

- FMZ source id: 440995 (lineage).
- Source: https://www.fmz.com/strategy/440995 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 15:42:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Fixed tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [150, 75] x `ema_len` [34, 17]: **4 trials**; MACD 9 / 17 / 9 and the ATR multiples fixed.

## Ambiguities resolved

- Fixed tick bracket as ATR multiples (29.2 / 17.8 at the 2-hour reading). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
