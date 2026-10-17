# #435003 基于ADXBB-BAO和EMA的量化交易策略Four-factor-Momentum-Tracking-Trading-Strategy-Based-on-ADX-BB-B-AO-and-EMA -> `fmz_435003_four_factor_bracket`

- FMZ source id: 435003 (lineage).
- Source: https://www.fmz.com/strategy/435003 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 16:24:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket fixed at entry (re-issued levels approximated) |
| 2 | ADAPT | The price-unit AO level -> an ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [15, 25] x `ao_atr` [0.002, 0.2]: **4 trials**; EMAs, BB 20 / 2 and the 5 % / 10 % bracket fixed.

## Ambiguities resolved

- AO level -> ATR multiple; re-issued bracket not ported (trailing_stop_pending). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
