# #431221 Connecticut Turtle System -> `fmz_431221_connecticut_turtle_long`

- FMZ source id: 431221 (lineage).
- Source: https://www.fmz.com/strategy/431221 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 10:23:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | Donchian breakouts and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity per entry and pyramiding 5 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_n` [2.0, 3.0] x `l1` [20, 40]: **4 trials**; L2 55, exits 10 / 20, pyramid 1 N fixed.

## Ambiguities resolved

- The skipped-after-win L1 trade is tracked as written; adds not ported but they move the stop. Long only.
  FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
