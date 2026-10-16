# #428581 MACD TrueLevel Strategy -> `fmz_428581_macd_truelevel_long`

- FMZ source id: 428581 (lineage).
- Source: https://www.fmz.com/strategy/428581 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:23:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.
- Duplicate group: **DG428581** (2 members, best partner #431501, Jaccard 0.855); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Regression bands in standard deviations. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428581. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_band` [12, 6] x `exit_band` [12, 6]: **4 trials**; defaults 12 / 12 (the source's; band 12 = 2646 bars, band 6 = 630 bars); MACD 12/26/9 and mult 1 fixed.

## Ambiguities resolved

- Only the selected bands reach the orders; TrueLevel max / min drawn. Shorts off: Long only.
- A same-bar close acts only on an open position. Long warm-up (2646 bars) as written. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
