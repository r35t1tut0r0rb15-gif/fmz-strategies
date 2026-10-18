# #435981 Momentum Capture Channel Strategy -> `fmz_435981_donchian_midline_exit`

- FMZ source id: 435981 (lineage).
- Source: https://www.fmz.com/strategy/435981 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 15:46:40). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Stop switch off by default: not ported |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`high_period` [10, 20] x `low_period` [10, 20]: **4 trials**.

## Ambiguities resolved

- Midline exit includes the current bar; stop off. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
