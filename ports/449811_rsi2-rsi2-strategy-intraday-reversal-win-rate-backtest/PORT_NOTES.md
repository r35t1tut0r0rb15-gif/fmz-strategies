# #449811 RSI2策略之日内反转胜率回测-RSI2-Strategy-Intraday-Reversal-Win-Rate-Backtest -> `fmz_449811_rsi2_dip_above_sma200_low_bracket_long`

- FMZ source id: 449811 (lineage).
- Source: https://www.fmz.com/strategy/449811 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 14:02:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar (re-sent levels marked) |
| 2 | PASS | RSI 2 dips in an uptrend with a low-based bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The qty 1 and margins stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_loss` [3.0, 1.5] x `target` [6.0, 3.0]: **4 trials**; the RSI length, the level and the SMA 200 fixed.

## Ambiguities resolved

- Levels from the signal bar's low; repeat-signal moves not followed. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
