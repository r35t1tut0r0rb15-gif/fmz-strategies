# #482775 高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System -> `fmz_482775_rsi30_70_recross_bb20_touch_basis_exit_reversal`

- FMZ source id: 482775 (lineage).
- Source: https://www.fmz.com/strategy/482775 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-touch RSI re-crossings with basis exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `bb_std_dev` [2.0, 1.5]: **4 trials**; RSI 14, 70 / 30.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
