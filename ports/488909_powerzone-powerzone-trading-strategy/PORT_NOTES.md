# #488909 PowerZone交易策略-PowerZone-Trading-Strategy -> `fmz_488909_powerzone_breakout_bracket`

- FMZ source id: 488909 (lineage).
- Source: https://www.fmz.com/strategy/488909 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 17:34:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Candle sequences and zone heights. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [5, 3] x `tp_factor` [1.5, 3.0]: **4 trials**; defaults 5 / 1.5 (the source's); threshold 0, bodies, SL
factor 1 fixed.

## Ambiguities resolved

- The zone bracket from the signal bar (re-based on the fill). Entries only from flat: simulate() follows the house
  bracket on bars. Opposite entries cannot occur.
- Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action_breakout"`.

## Marks

`coarse_bar_stop`
