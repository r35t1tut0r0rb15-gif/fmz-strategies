# #436499 Double Bollinger Bands Breakout Strategy -> `fmz_436499_double_bollinger_breakout`

- FMZ source id: 436499 (lineage).
- Source: https://www.fmz.com/strategy/436499 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 13:20:31). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | REVIEW | Optional bracket inputs default to off |
| 2 | PASS | Band breakout |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the optional bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`l` [100, 50] x `pbin` [0.25, 0.5]: **4 trials**; outer 1.5 fixed.

## Ambiguities resolved

- Optional exits are off by default and not ported. Orders in call order. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
