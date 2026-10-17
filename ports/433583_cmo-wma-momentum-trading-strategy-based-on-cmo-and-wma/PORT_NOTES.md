# #433583 基于CMO和WMA的动量交易策略Momentum-Trading-Strategy-Based-on-CMO-and-WMA -> `fmz_433583_cmo_vs_wma`

- FMZ source id: 433583 (lineage).
- Source: https://www.fmz.com/strategy/433583 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-28 16:42:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A bounded momentum ratio against its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430117. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 18] x `wma_len` [9, 18]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
