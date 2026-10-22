# #445467 基于动态多均线与MACD指标的XAUUSD交易策略Dynamic-Multi-SMA-and-MACD-based-XAUUSD-Trading-Strategy -> `fmz_445467_sma15_45_cross_trend_macd_atr_bracket_reversal`

- FMZ source id: 445467 (lineage).
- Source: https://www.fmz.com/strategy/445467 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-19 17:34:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | SMA crossings with trend and MACD filters, ATR bracket |
| 3 | PASS | Exchange pair in the header only; XAUUSD in the title only. |
| 4 | DONE | The 10 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.0, 1.5] x `trend_len` [100, 200]: **4 trials**; the 2 : 1 target ratio, the fast / slow SMAs and the MACD fixed.

## Ambiguities resolved

- Levels from the signal bar; repeat-signal moves not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
