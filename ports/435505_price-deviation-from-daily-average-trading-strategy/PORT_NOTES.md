# #435505 Price Deviation from Daily Average Trading Strategy -> `fmz_435505_ichimoku_two_entry_types`

- FMZ source id: 435505 (lineage).
- Source: https://www.fmz.com/strategy/435505 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 15:44:18). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud and line rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [20, 9] x `base` [60, 26]: **4 trials**; span B 120 and displacement 30 fixed.

## Ambiguities resolved

- Per-id closes; one trade per direction; orders in call order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
