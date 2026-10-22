# #439695 快速响应型加密货币RSI趋势跟踪策略Crypto-RSI-Mini-Sniper-Quick-Response-Trend-Following-Strategy -> `fmz_439695_rsi_mini_sniper_sma400_bracket`

- FMZ source id: 439695 (lineage).
- Source: https://www.fmz.com/strategy/439695 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 10:46:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | RSI levels and an SMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.05, 0.03] x `sl` [0.02, 0.01]: **4 trials**; RSI 14 at 35 / 65 / 80 / 20 and SMA 400 fixed.

## Ambiguities resolved

- Bracket from the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
