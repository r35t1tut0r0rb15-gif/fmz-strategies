# #488527 多指标联动SAR反转策略与过滤入场模型-Multi-Indicator-Synergistic-SAR-Reversal-Strategy-with-Filtered-Entry-Model -> `fmz_488527_sar_flip_rsi_macd_stoch_lsma`

- FMZ source id: 488527 (lineage).
- Source: https://www.fmz.com/strategy/488527 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 16:36:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | SAR, oscillators and a regression line. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_max` [0.2, 0.1] x `lsma_offset` [9, 4]: **4 trials**; defaults 0.2 / 9 (the source's); SAR 0.02 / 0.02, RSI 14,
stoch RSI 14 and LSMA 4 fixed.

## Ambiguities resolved

- `ta.sar` as #428699; `ta.stoch(rsi, rsi, rsi, 14)` is na on a flat window; `ta.linreg(close, 4, 0)` at the current
  bar. The close before each entry is the reversal (REVERSAL INTENDED). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
