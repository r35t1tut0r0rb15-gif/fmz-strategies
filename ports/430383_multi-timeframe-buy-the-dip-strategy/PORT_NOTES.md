# #430383 Multi Timeframe Buy the Dip Strategy -> `fmz_430383_coinrule_buy_the_dip_long`

- FMZ source id: 430383 (lineage).
- Source: https://www.fmz.com/strategy/430383 (PineScript v1, author ChaoZhang, FMZ last
  modified 2023-10-27 16:56:23). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Percentage changes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 30 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430383. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lkb_long` [24, 48] x `stop_pct` [3.0, 5.0]: **4 trials**; look-back 2, rise 3 %, dip 1 %, target 4 % fixed.

## Ambiguities resolved

- Close-checked stop / target from the fill. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
