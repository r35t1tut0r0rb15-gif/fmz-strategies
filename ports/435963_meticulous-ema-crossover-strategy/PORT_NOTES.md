# #435963 Meticulous EMA Crossover Strategy -> `fmz_435963_ema_13_48_cross_long_stop`

- FMZ source id: 435963 (lineage).
- Source: https://www.fmz.com/strategy/435963 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-20 14:28:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | REVIEW | Trailing inputs unused; stop from the 1.08 divisor |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, pyramiding and trailing inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435963. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 8] x `slow` [48, 34]: **4 trials**; the stop 1 - 1/1.08 fixed.

## Ambiguities resolved

- Stop at avg / 1.08; trail inputs unused. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
