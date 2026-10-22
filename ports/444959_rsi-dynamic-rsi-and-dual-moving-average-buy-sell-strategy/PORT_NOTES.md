# #444959 动态RSI双均线买卖策略Dynamic-RSI-and-Dual-Moving-Average-Buy-Sell-Strategy -> `fmz_444959_rsi2_extremes_sma200_side_atr_stop_reversal`

- FMZ source id: 444959 (lineage).
- Source: https://www.fmz.com/strategy/444959 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 14:36:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | RSI 2 extremes with an SMA side filter; tick stop as an ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the tick inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [3.33, 1.0] x `sma_len` [200, 100]: **4 trials**; the RSI levels and the EMAs fixed.

## Ambiguities resolved

- Tick stop as 3.33 ATR(14); no trail (offset na); target out of reach. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
