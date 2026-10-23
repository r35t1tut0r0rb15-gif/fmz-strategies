# #458143 Multi Confirmation Reversal Buy Strategy -> `fmz_458143_dip_buy_breakout_bar_10bar_exit_long_only`

- FMZ source id: 458143 (lineage).
- Source: https://www.fmz.com/strategy/458143 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 12:06:29). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 10-bar time exit |
| 2 | PASS | Breakout bars in an SMA uptrend with RSI and volume confirmation |
| 3 | PASS | No exchange header; no symbol named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [10, 20] x `lookback` [3, 5]: **4 trials**; SMA 10 / 20, RSI 14, volume SMA 5.

## Ambiguities resolved

- No header: bar size searched. Volume = broker tick volume. Long only. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback_time_exit"`.

## Marks

`bar_size_pending`
