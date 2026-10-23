# #489033 US30多级趋势确认与风险管理策略-US30-Multi-Grade-Trend-Confirmation-Risk-Management-Strategy -> `fmz_489033_ema_sma_cross_graded_body_volume_pct_bracket_1h_reversal`

- FMZ source id: 489033 (lineage).
- Source: https://www.fmz.com/strategy/489033 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 13:41:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA / SMA crossings in the EMA 200 trend graded by body size and volume |
| 3 | PASS | Exchange pair in the header only (US30 named in the title). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.5, 1.0] x `sl_pct` [0.3, 0.6]: **4 trials**; RSI 9, MA 20, EMA 200, grades A and B.

## Ambiguities resolved

- Grade A precedence as written (RSI < 45 alone passes a short). Repeats re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
