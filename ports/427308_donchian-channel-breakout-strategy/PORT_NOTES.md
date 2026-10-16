# #427308 Donchian Channel Breakout Strategy -> `fmz_427308_donchian_close_breakout_long`

- FMZ source id: 427308 (lineage).
- Source: https://www.fmz.com/strategy/427308 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 21:47:41). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.
- Near-duplicate group: **ND427308** (3 members, best partner #443123, Jaccard 0.790); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427308. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 10, 55]: **3 trials**; default 20 (the source's constant).

## Ambiguities resolved

- The channel is of closes and excludes the current bar ([1]). Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
