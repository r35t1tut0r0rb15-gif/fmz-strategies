# #439962 Intelligent Trailing Stop Loss Strategy -> `fmz_439962_lucid_sar_flip_as_written`

- FMZ source id: 439962 (lineage).
- Source: https://www.fmz.com/strategy/439962 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 12:50:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR recursion |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`af_increment` [0.02, 0.01] x `af_maximum` [0.2, 0.1]: **4 trials**; AF initial 0.02 fixed.

## Ambiguities resolved

- Short on every flip bar, as written. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
