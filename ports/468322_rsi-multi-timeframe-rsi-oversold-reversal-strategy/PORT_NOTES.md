# #468322 多周期RSI超卖反转策略-Multi-Timeframe-RSI-Oversold-Reversal-Strategy -> `fmz_468322_rsi11_oversold_rsi79_or_signal_close_target_long`

- FMZ source id: 468322 (lineage).
- Source: https://www.fmz.com/strategy/468322 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:38:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target is a close test |
| 2 | PASS | RSI oversold entries with RSI and percent exits |
| 3 | PASS | Exchange pair in the header only (gold named in the title). |
| 4 | DONE | The 3-unit add-on quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [11, 14] x `entry_th` [20, 30] x `tp_pct` [0.035, 0.02]: **8 trials**; the RSI 79 exit fixed.

## Ambiguities resolved

- Target from the latest signal close; the add-on entry from flat as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
