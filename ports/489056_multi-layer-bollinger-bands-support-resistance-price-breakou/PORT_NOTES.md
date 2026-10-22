# #489056 Multi Layer Bollinger Bands Support Resistance Price Breakout Trading Strategy -> `fmz_489056_bb20_2_outside_retouched_sr_pip_stop_flat`

- FMZ source id: 489056 (lineage).
- Source: https://www.fmz.com/strategy/489056 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 16:55:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar stop as a fraction of the fill |
| 2 | ADAPT | Pip distances read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Margins stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sr_pips` [25, 100] x `stop_pips` [15, 60]: **4 trials**; BB 20 / 2; pips at 0.1 / 3000 of the price.

## Ambiguities resolved

- Only the stop is live (the target is na), as written; pips read at ETH 3000. Entries only from flat. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`
