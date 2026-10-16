# #427679 DiNapoli Detrended Oscillator Strategy -> `fmz_427679_hpotter_dinapoli_detrended_rev`

- FMZ source id: 427679 (lineage).
- Source: https://www.fmz.com/strategy/427679 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-23 15:48:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Close minus its average, zero trigger. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7, 28, 50]: **4 trials**; default 14 (the source's); trigger 0 and reverse = true fixed.

## Ambiguities resolved

- "Trade reverse" defaults to true in the source and is kept: above the SMA is short.
- No order while the SMA is na. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
