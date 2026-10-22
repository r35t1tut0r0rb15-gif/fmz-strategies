# #472246 Dual Moving Average Crossover Strategy with Dynamic Risk Management -> `fmz_472246_sma9_21_cross_1_2pct_bracket_reversal`

- FMZ source id: 472246 (lineage).
- Source: https://www.fmz.com/strategy/472246 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-18 15:54:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only (BTCUSD named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50] x `tp_pct` [0.02, 0.04]: **8 trials**; the 1 % stop fixed.

## Ambiguities resolved

- Header's 1-hour bars followed (the title says daily). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
