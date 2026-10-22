# #445840 Donchian Channel Breakout Strategy with ATRSL Trailing Stop -> `fmz_445840_donchian100_break_atr_trail_cross_long`

- FMZ source id: 445840 (lineage).
- Source: https://www.fmz.com/strategy/445840 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 16:13:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian breakout with an ATR trailing-line exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`don_len` [100, 55] x `atr_mult` [3.0, 2.0]: **4 trials**; the ATR period fixed.

## Ambiguities resolved

- Previous bar's channel; trailing line as a close crossing. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
