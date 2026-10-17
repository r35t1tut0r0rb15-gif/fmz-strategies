# #435155 Bollinger Band Awesome Oscillator Breakout Trading Strategy -> `fmz_435155_ema2_bb_basis_ao_long`

- FMZ source id: 435155 (lineage).
- Source: https://www.fmz.com/strategy/435155 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-12 17:47:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses and an oscillator slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [5, 20] x `fast` [2, 3]: **4 trials**; AO 5 / 34 fixed.

## Ambiguities resolved

- AO slope state as written; date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
