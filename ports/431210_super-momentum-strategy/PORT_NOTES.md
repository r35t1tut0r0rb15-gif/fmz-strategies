# #431210 Super Momentum Strategy -> `fmz_431210_super_momentum_cmo_rmi`

- FMZ source id: 431210 (lineage).
- Source: https://www.fmz.com/strategy/431210 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 09:24:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmo_len` [9, 20] x `cmo_buy` [25, 35]: **4 trials**; CMO sell line = 100 - buy line; the five RMIs and their lines fixed.

## Ambiguities resolved

- RMI2 / RMI5 quirks as written. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
