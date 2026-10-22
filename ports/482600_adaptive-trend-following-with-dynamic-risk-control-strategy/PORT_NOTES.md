# #482600 Adaptive Trend Following with Dynamic Risk Control Strategy -> `fmz_482600_sar_cross_ema50_rsi_resent_atr_pct_bracket_flat_only`

- FMZ source id: 482600 (lineage).
- Source: https://www.fmz.com/strategy/482600 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 11:26:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; re-sent bracket followed in the loop (pending) |
| 2 | PASS | SAR crossings with EMA and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.3, 2.0] x `take_profit_percent` [0.007, 0.015]: **4 trials**; SAR 0.02 / 0.02 / 0.2, EMA 50, RSI 14.

## Ambiguities resolved

- The re-sent bracket is pending; the loop closes on the touching bar's close, one bar late.
- Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`trailing_stop_pending`
