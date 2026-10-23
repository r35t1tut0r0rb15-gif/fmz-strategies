# #437561 Price Momentum Tracking Strategy -> `fmz_437561_vwap_swma_momentum_setup_tick_bracket_long`

- FMZ source id: 437561 (lineage).
- Source: https://www.fmz.com/strategy/437561 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 17:32:14). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed fractional bracket from the fill |
| 2 | PASS | VWAP and SWMA momentum re-entries |
| 3 | PASS | Exchange pair in the header only; tick distances converted at the source's BTC price. |
| 4 | DONE | Strategy(): 100 % of equity, capital 20000, commission 0.025 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.000595, 0.002] x `sl` [0.00595, 0.01]: **4 trials**.

## Ambiguities resolved

- Swapped profit / loss inputs, as written; ticks converted at about 42000 USD BTC. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
