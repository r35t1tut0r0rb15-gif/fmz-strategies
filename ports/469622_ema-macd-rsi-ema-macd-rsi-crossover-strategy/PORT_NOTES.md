# #469622 EMA-MACD-RSI-交叉策略-EMA-MACD-RSI-Crossover-Strategy -> `fmz_469622_ema3_4_or_macd123_cross_rsi42_atr_stop_reversal`

- FMZ source id: 469622 (lineage).
- Source: https://www.fmz.com/strategy/469622 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-10-14 12:22:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at entry |
| 2 | PASS | Fast EMA / MACD crossings with an RSI filter and an ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [42, 14] x `atr_mult` [1.0, 2.0]: **4 trials**; the EMA and MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
