# #488909 PowerZone交易策略-PowerZone-Trading-Strategy -> `fmz_488909_powerzone5_breakout_zone_bracket_flat`

- FMZ source id: 488909 (lineage).
- Source: https://www.fmz.com/strategy/488909 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 17:34:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C268). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; zone bracket as fractions of the fill |
| 2 | PASS | Order-block (PowerZone) breakouts with a zone bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [5, 3] x `tp_factor` [1.5, 3.0]: **4 trials**; SL 1.0 zone height.

## Ambiguities resolved

- Entries only from flat (a loop follows the bracket on the bar's high / low). FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "order_block"`.

## Marks

`coarse_bar_stop`
