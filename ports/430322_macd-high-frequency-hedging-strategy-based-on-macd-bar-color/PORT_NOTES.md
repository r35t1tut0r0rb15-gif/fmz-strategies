# #430322 基于MACD柱色和线性回归的高频对冲策略High-Frequency-Hedging-Strategy-Based-on-MACD-Bar-Color-and-Linear-Regression -> `fmz_430322_sonic_r_linreg_macd`

- FMZ source id: 430322 (lineage).
- Source: https://www.fmz.com/strategy/430322 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-27 10:42:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages, a regression line and MACD states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_signal` [89, 50] x `hilo_len` [34, 20]: **4 trials**; linreg length = ema_signal; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Closes act on the start position unless reversed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
