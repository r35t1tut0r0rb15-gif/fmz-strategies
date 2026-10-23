# #437032 Volume Weighted Average Price Strategy -> `fmz_437032_cumulative_vwap_cross_close_bracket_reversal`

- FMZ source id: 437032 (lineage).
- Source: https://www.fmz.com/strategy/437032 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 16:31:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target and stop in the signals |
| 2 | PASS | Crossings of a cumulative VWAP |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.03, 0.05] x `sl` [0.01, 0.02]: **4 trials**.

## Ambiguities resolved

- VWAP from the first loaded bar (data-start dependent). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
