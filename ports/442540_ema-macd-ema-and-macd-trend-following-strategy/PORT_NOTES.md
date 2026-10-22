# #442540 基于EMA和MACD的趋势跟踪策略EMA-and-MACD-Trend-Following-Strategy -> `fmz_442540_ema20_cross_macd_confirm_unit_bracket`

- FMZ source id: 442540 (lineage).
- Source: https://www.fmz.com/strategy/442540 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 16:28:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit bracket -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [20, 50] x `risk_frac` [0.000238, 0.0024]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Price-unit bracket as fractions of the fill; a repeat signal's move not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
