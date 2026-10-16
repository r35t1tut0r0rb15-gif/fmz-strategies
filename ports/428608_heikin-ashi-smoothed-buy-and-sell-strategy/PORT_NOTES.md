# #428608 Heikin Ashi Smoothed Buy and Sell Strategy -> `fmz_428608_smoothed_heikin_ashi_long`

- FMZ source id: 428608 (lineage).
- Source: https://www.fmz.com/strategy/428608 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 15:01:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA length only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_period` [65, 30, 45, 100]: **4 trials**; default 65 (the source's).

## Ambiguities resolved

- last_signal carries itself through [1]; signals alternate. Long only.
- 2-day blocks of broker days (worker A's convention). FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi"`.

## Marks

`none`
