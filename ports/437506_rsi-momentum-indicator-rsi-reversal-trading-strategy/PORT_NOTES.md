# #437506 动量指标RSI捕捉反转交易策略Momentum-Indicator-RSI-Reversal-Trading-Strategy -> `fmz_437506_rsi_breakout_adx_smma_3h`

- FMZ source id: 437506 (lineage).
- Source: https://www.fmz.com/strategy/437506 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-03 12:09:48). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 3-hour values end with the daily bar |
| 2 | PASS | RSI levels, ADX and SMMA directions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smma_len` [20, 40] x `adx_len` [14, 21]: **4 trials**; DI 14, RSI 7, levels 68 / 28 and the 180-minute frame fixed.

## Ambiguities resolved

- 3-hour values = the day's last 3-hour bar from the broker day's start; RSI hard-coded 7. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
