# #437808 基于ATR和标准差通道的趋势跟踪交易策略ATR-Trend-Following-Strategy-Based-on-Standard-Deviation-Channel -> `fmz_437808_atr_trail_line_inverted`

- FMZ source id: 437808 (lineage).
- Source: https://www.fmz.com/strategy/437808 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-05 16:34:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [0.5, 1.0] x `atr_period` [11, 22]: **4 trials**.

## Ambiguities resolved

- Inverted crossing signs as written; the exit without levels places no order. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
