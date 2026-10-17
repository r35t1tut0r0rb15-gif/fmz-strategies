# #488143 相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy -> `fmz_488143_rsi_band_reentry`

- FMZ source id: 488143 (lineage).
- Source: https://www.fmz.com/strategy/488143 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 14:22:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity and the MT4 lot input quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 21] x `band` [30, 25]: **4 trials**; defaults 14 / 30 (the source's; the upper level is 100 - band,
70 by default).

## Ambiguities resolved

- The MetaTrader alert strings (inputs before `strategy()`, which FMZ accepted) only feed alerts: not ported.
- Closes act on the position at the bar's start (#430850); a short signal while long reverses. REVERSAL INTENDED.
  Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
