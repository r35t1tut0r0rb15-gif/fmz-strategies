# #427734 Multi Momentum Indicators Combo Strategy -> `fmz_427734_chande_zero_cross_rmi_hull_vwma_ema_rsi_agreement_reversal`

- FMZ source id: 427734 (lineage).
- Source: https://www.fmz.com/strategy/427734 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-24 13:24:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Chande momentum zero crossings confirmed by RSI-family oscillators |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmo_length` [9, 14] x `rmi_length` [30, 20]: **4 trials**; RMI momentum 25, RSI 14, MA 7.

## Ambiguities resolved

- Every level 0 as the defaults. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_threshold"`.

## Marks

`none`
