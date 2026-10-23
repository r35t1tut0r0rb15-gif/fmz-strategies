# #433099 Dual Moving Average Arbitrage Strategy -> `fmz_433099_reversal123_finite_volume_elements_combo_reversal`

- FMZ source id: 433099 (lineage).
- Source: https://www.fmz.com/strategy/433099 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 14:21:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and volume-element states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fve_period` [18, 30] x `factor` [0.6, 0.3]: **4 trials**; 123 reversal 15 / 1 / 3 / 50.

## Ambiguities resolved

- Volume = broker tick volume (FVE). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
