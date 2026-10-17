# #431967 EMA百分比通道与布林带区间交易策略EMA-Percentage-Channel-with-Bollinger-Band-Range-Trading-Strategy -> `fmz_431967_ema_channel_bb_range`

- FMZ source id: 431967 (lineage).
- Source: https://www.fmz.com/strategy/431967 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 17:38:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (rule 2) |
| 2 | PASS | An EMA percentage channel, Bollinger bands and an ATR band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel_pct` [1.0, 2.0] x `atr_mult` [1.75, 3.0]: **4 trials**; EMA 200, BB 20 / 2 and ATR 14 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the bracket re-issued at the current band and ATR band; fixed at the signal bar.
  REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
