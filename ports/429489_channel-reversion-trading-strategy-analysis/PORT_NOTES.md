# #429489 Channel Reversion Trading Strategy Analysis -> `fmz_429489_keltner_reentry_bracket`

- FMZ source id: 429489 (lineage).
- Source: https://www.fmz.com/strategy/429489 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 15:48:36). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Channel levels from the bars (true-range multiples). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 10 % of equity stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [1.5, 2.0] x `kc_sl_mult` [3.0, 2.5]: **4 trials**; Keltner 35 and the entry type fixed.

## Ambiguities resolved

- Default Keltner / entry / stop / target options only. Flat tracked through the bracket.
- Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`
