# #458057 RSI-反转交叉动量盈利目标量化交易策略-RSI-Reversal-Cross-Momentum-Profit-Target-Quantitative-Trading-Strategy -> `fmz_458057_rsi_extreme_reentry_close_profit_target_reversal`

- FMZ source id: 458057 (lineage).
- Source: https://www.fmz.com/strategy/458057 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 15:56:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the profit target is a close test against the fill |
| 2 | PASS | RSI re-entries from extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trade size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `target_frac` [0.00238, 0.01]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Profit target as a fraction of 42000; no stop. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
