# #451387 EMAMACDRSI三重指标动量策略-EMA-MACD-and-RSI-Triple-Indicator-Momentum-Strategy -> `fmz_451387_ema21_side_rsi_hist_two_pct_bracket_reversal`

- FMZ source id: 451387 (lineage).
- Source: https://www.fmz.com/strategy/451387 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 15:34:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA side with RSI and MACD agreement, percent bracket |
| 3 | PASS | Exchange pair in the header only; the alert text names XAUUSDm as a message only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [21, 50] x `bracket` [0.02, 0.04]: **4 trials**; the RSI and MACD settings fixed.

## Ambiguities resolved

- Bracket from the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
