# #474668 基于布林带和ATR的多级智能动态跟踪止损策略-Multi-Level-Intelligent-Dynamic-Trailing-Stop-Strategy-Based-on-Bollinger-Bands-and-ATR -> `fmz_474668_bb20_1p5_dip_green_close_stop_atr_ratchet_long`

- FMZ source id: 474668 (lineage).
- Source: https://www.fmz.com/strategy/474668 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 14:52:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-dip reversal candles with close-based stop and ATR ratchet |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `atr_mult` [1.0, 2.0]: **4 trials**; band 1.5 sd, SMA basis.

## Ambiguities resolved

- Levels re-set by repeat signals while long, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
