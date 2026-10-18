# #436136 Bollinger Bands Based High Frequency Trading Strategy -> `fmz_436136_basis_upcross_long_target`

- FMZ source id: 436136 (lineage).
- Source: https://www.fmz.com/strategy/436136 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 15:37:07). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target -> fraction of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity and starting amount stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `tp_frac` [0.1, 0.005]: **4 trials**.

## Ambiguities resolved

- Tick target -> fraction (both readings in the grid); no stop. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
