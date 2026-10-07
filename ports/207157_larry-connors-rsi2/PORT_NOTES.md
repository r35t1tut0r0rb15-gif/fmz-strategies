# #207157 Larry-Connors-RSI2均值回归策略 -> `fmz_207157_rsi2_extremes_vs_sma`

- Source: https://www.fmz.com/strategy/207157 (MyLanguage, author homily, FMZ last modified
  2020-05-14 09:50:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | PASS | RSI thresholds and an MA side test only. |
| 3 | PASS | OKCoin quarterly contract in the header only. |
| 4 | DONE | Lot `liang` (equity x previous close / 100) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`y` [50, 70, 100, 200] x `band` [5, 10] (RSI2 below `band` / above 100-`band`) = **8 trials**.

## Ambiguities resolved

- **As written vs the cited rule**: the code shorts RSI2>90 above the MA and buys RSI2<10 below
  it, the opposite of Connors' published RSI2 rule that the source's comments link to. The port
  follows the code. A "Connors as published" variant is not made (rule 5's twin-module rule is
  only for stop=/limit= entries); flagged in the worker report.
- Exits require the same MA side as their entry's opposite line; kept.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"` (as #11604).

## Marks (2026-10-07)

`none`
