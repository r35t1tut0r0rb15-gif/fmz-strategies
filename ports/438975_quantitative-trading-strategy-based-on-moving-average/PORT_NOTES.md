# #438975 Quantitative Trading Strategy Based on Moving Average -> `fmz_438975_oracle_hull_style_cross`

- FMZ source id: 438975 (lineage).
- Source: https://www.fmz.com/strategy/438975 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-16 17:37:13). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull-style average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [30, 60] x `mode` ["wma", "ema"]: **4 trials**.

## Ambiguities resolved

- Mode swept over wma / ema. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
