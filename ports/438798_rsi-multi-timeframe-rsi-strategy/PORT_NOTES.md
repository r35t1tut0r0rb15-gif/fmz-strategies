# #438798 多时间框架RSI策略Multi-Timeframe-RSI-Strategy -> `fmz_438798_mtf_rsi_15_60_240`

- FMZ source id: 438798 (lineage).
- Source: https://www.fmz.com/strategy/438798 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 14:15:32). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSIs on three bar sizes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438798. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `tf_mid` [60, 30]: **4 trials**; 15- and 240-minute sizes fixed.

## Ambiguities resolved

- Lower-timeframe RSIs = the day's last bar of each size. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
