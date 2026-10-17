# #432789 双EMA黄金交叉趋势追踪策略Dual-EMA-Golden-Cross-Trend-Tracking-Strategy -> `fmz_432789_ema_21_55_atr_bracket`

- FMZ source id: 432789 (lineage).
- Source: https://www.fmz.com/strategy/432789 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-21 15:10:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA crosses and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 3.0] x `tp_atr` [1.0, 3.0]: **4 trials**; EMA 21 / 55 and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the signal bar's open, re-based on the fill. Sessions always open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
