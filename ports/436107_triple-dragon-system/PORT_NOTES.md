# #436107 Triple Dragon System -> `fmz_436107_epvt_sarx_cross_level_breakout_reversal`

- FMZ source id: 436107 (lineage).
- Source: https://www.fmz.com/strategy/436107 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 11:56:31). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Crossings of signal-cross price levels (EPVT and SAR) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1000, commission 0.01 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`epvt_len` [200, 100] x `sar_max` [0.8, 0.2]: **4 trials**; SAR start / increment 0.02, ATR 14.

## Ambiguities resolved

- Script SAR-X stepped by ATR. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "level_breakout"`.

## Marks

`none`
