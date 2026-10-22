# #482489 双均线趋势交叉结合ADX动量过滤的自适应风险策略-Adaptive-Risk-Strategy-with-Dual-EMA-Crossover-and-ADX-Momentum-Filter -> `fmz_482489_ema50_cross_ema200_adx25_di_swing5_atr_bracket_reversal`

- FMZ source id: 482489 (lineage).
- Source: https://www.fmz.com/strategy/482489 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 16:21:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing / ATR bracket as fractions of the fill |
| 2 | PASS | EMA pullback crossings in an ADX / DI trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 / 100 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25, 20] x `risk_reward` [1.5, 2.5]: **4 trials**; EMA 50 / 200, DMI 14, swing 5, ATR 14 x 0.5.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`trailing_stop_pending`
