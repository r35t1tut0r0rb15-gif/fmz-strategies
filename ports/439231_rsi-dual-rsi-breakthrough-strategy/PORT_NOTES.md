# #439231 双RSI突破量化交易策略Dual-RSI-Breakthrough-Strategy -> `fmz_439231_noro_double_rsi_colour_exit`

- FMZ source id: 439231 (lineage).
- Source: https://www.fmz.com/strategy/439231 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-18 15:25:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and bar colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity / close lot and leverage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [2, 3] x `slow` [14, 21]: **4 trials**.

## Ambiguities resolved

- Opposite signal reverses unless the bar has the exit colour (then flat). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
