# #484595 Multi Indicator Trend Confirmation Momentum Trading Strategy -> `fmz_484595_ema20_50_cross_rsi_macd_ema200_confirm_long`

- FMZ source id: 484595 (lineage).
- Source: https://www.fmz.com/strategy/484595 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 10:35:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with RSI / MACD / EMA 200 confirmation |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**; EMA 200, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
