# #439639 动态CCI支撑阻力策略Dynamic-CCI-Support-and-Resistance-Strategy -> `fmz_439639_cci_pivot_support_resistance_atr_bracket`

- FMZ source id: 439639 (lineage).
- Source: https://www.fmz.com/strategy/439639 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 16:37:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | CCI pivots mapped to price, EMA trend and ATR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ksl` [1.1, 2.0] x `ktp` [2.2, 4.0]: **4 trials**; CCI 50, pivots 50 / 50, buffer 10 and EMA 50 / 100 fixed.

## Ambiguities resolved

- Previous day's largest ATR from the module's bars; bracket from the signal bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
