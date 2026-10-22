# #441137 基于RSI动态加仓策略RSI-Dynamic-Position-Averaging-Strategy -> `fmz_441137_rsi30_dip_close_target_long`

- FMZ source id: 441137 (lineage).
- Source: https://www.fmz.com/strategy/441137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 09:44:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level and close-vs-fill target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash quantity rules stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [30, 20] x `target` [0.005, 0.01]: **4 trials**; RSI 14 fixed.

## Ambiguities resolved

- Default pyramiding refuses the martingale adds. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
