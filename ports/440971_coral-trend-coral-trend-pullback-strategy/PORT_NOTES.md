# #440971 基于回测试区间Coral-Trend指标的瑞波策略Coral-Trend-Pullback-Strategy -> `fmz_440971_coral_trend_pullback_adx_di_swing_bracket_3m_reversal`

- FMZ source id: 440971 (lineage).
- Source: https://www.fmz.com/strategy/440971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 12:18:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing-based bracket from the signal bar as fractions of the fill |
| 2 | PASS | Coral Trend pullback re-entries confirmed by ADX / DI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 1 % / stop % / close, commission 0.02 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ct_sm` [25, 50] x `risk_reward` [1.5, 2.0]: **4 trials**; constant D 0.4, ADX 14 / 20, lookback 5.

## Ambiguities resolved

- Bracket fixed at the signal bar; the script's own in-trade flags gate entries as written. Volume not used. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_pullback"`.

## Marks

`none`
