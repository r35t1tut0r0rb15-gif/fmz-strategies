# #427470 ATR Trend Following Strategy -> `fmz_427470_atr_trailing_line_state`

- FMZ source id: 427470 (lineage).
- Source: https://www.fmz.com/strategy/427470 (PineScript, no @version line, v5 syntax; author ChaoZhang, FMZ
  last modified 2023-09-21 15:13:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the "trailing stop" is a line compared with closes. |
| 2 | PASS | ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission setting stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [5, 10, 14] x `atr_mult` [3.5, 2]: **6 trials**; defaults 5 / 3.5 (the source's).

## Ambiguities resolved

- No stop order: the line only decides the side (close above = long). Broker-day bars.
- REVERSAL INTENDED. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
