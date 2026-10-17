# #431891 Bollinger Breakout Strategy -> `fmz_431891_noro_bollinger_fade`

- FMZ source id: 431891 (lineage).
- Source: https://www.fmz.com/strategy/431891 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-13 10:19:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | Bollinger bands and bar colour / body filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and pyramiding 5 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**; source ohlc4 and the body filter fixed.

## Ambiguities resolved

- Body filter on the short exit only (Pine precedence); close_all after an entry leaves the bar flat. REVERSAL INTENDED.
  FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
