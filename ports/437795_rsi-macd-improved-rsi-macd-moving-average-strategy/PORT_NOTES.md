# #437795 均线黄金交叉RSI-MACD策略Improved-RSI-MACD-Moving-Average-Strategy -> `fmz_437795_rsi_macd_ema_atr_long`

- FMZ source id: 437795 (lineage).
- Source: https://www.fmz.com/strategy/437795 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 16:11:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested exits |
| 2 | PASS | MACD, RSI, EMAs and ATR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.09, 0.05] x `atr_mult` [2.0, 1.0]: **4 trials**; MACD 12 / 26 / 9, RSI 14, EMA 8 / 21, ATR 20 and target 0.15 fixed.

## Ambiguities resolved

- Close-tested trail from the last condition bar; take-profit test as written (17.6 %). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
