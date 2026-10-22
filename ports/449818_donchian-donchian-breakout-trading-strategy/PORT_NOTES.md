# #449818 Donchian突破交易策略-Donchian-Breakout-Trading-Strategy -> `fmz_449818_donchian20_flat_edge_break_basis_stop_rr5_reversal`

- FMZ source id: 449818 (lineage).
- Source: https://www.fmz.com/strategy/449818 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 14:56:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; levels from the signal bar's basis and the fill |
| 2 | PASS | Donchian breakouts with a basis stop and RR target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`don_length` [20, 55] x `rr` [5.0, 2.0]: **4 trials**.

## Ambiguities resolved

- "New" edge test as written; stop from |fill - basis|. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop`
