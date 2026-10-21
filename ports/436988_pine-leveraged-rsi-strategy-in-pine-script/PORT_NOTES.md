# #436988 在Pine脚本中设置杠杆策略Leveraged-RSI-Strategy-in-Pine-Script -> `fmz_436988_rsi_band_reentry`

- FMZ source id: 436988 (lineage).
- Source: https://www.fmz.com/strategy/436988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 10:46:35). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leverage quantity, percent of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `over_sold` [30, 20]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- Leverage sizing stored. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
