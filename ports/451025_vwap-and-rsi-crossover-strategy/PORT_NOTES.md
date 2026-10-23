# #451025 VWAP and RSI Crossover Strategy -> `fmz_451025_rolling_vwap20_cross_rsi20_2d_reversal`

- FMZ source id: 451025 (lineage).
- Source: https://www.fmz.com/strategy/451025 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-05-11 11:42:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling-VWAP crossings with RSI limits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Entry qty 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vwap_period` [20, 10] x `rsi_period` [20, 14]: **4 trials**; RSI 70 / 30.

## Ambiguities resolved

- Exits without prices never act. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "2D" (2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
