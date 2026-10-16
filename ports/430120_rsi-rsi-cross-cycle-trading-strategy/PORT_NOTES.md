# #430120 RSI跨周期交易策略RSI-Cross-Cycle-Trading-Strategy -> `fmz_430120_smoothed_rsi_turn_pct_exits`

- FMZ source id: 430120 (lineage).
- Source: https://www.fmz.com/strategy/430120 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-25 11:20:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | RSI levels and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity / hlc3 per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.0, 1.0] x `tp_pct` [5.0, 2.5]: **4 trials**; RSI 14, SMA 14 and levels 70 / 30 fixed.

## Ambiguities resolved

- Close-checked SL / TP from the signal close. An opposite signal reverses. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
