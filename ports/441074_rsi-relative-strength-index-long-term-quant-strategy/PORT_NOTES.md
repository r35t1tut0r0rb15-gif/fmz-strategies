# #441074 基于RSI的长线量化策略Relative-Strength-Index-Long-term-Quant-Strategy -> `fmz_441074_rsi_under_40_entry_close_toggle_long`

- FMZ source id: 441074 (lineage).
- Source: https://www.fmz.com/strategy/441074 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 13:51:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level (entry and close in call order) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `rs_value` [40, 30]: **4 trials**.

## Ambiguities resolved

- Same-bar entry and close in call order, as written. Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
