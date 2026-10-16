# #428075 Combining DMI and Moving Average Trading Strategy -> `fmz_428075_hpotter_dmi_ma_cross`

- FMZ source id: 428075 (lineage).
- Source: https://www.fmz.com/strategy/428075 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-28 12:39:44). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA and DMI lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [30, 50] x `length_dmi` [14, 7]: **4 trials**; defaults 30 / 14 (the source's).

## Ambiguities resolved

- Both crosses on the same bar (strict on both sides, as written). "Trade reverse" fixed off.
- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "dmi_trend"`.

## Marks

`none`
