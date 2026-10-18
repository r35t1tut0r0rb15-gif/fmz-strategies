# #435720 基于05赫氏变化的短周期交易策略Heikin-Ashi-05-Change-Short-Period-Trading-Strategy -> `fmz_435720_half_percent_move_reversal`

- FMZ source id: 435720 (lineage).
- Source: https://www.fmz.com/strategy/435720 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 12:13:56). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [0.005, 0.01]: **2 trials**.

## Ambiguities resolved

- Side record var; plain closes. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
