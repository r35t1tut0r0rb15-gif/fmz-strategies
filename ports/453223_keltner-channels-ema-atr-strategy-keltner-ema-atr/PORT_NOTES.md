# #453223 Keltner-Channels-EMA-ATR-Strategy-Keltner通道EMA-ATR策略 -> `fmz_453223_keltner21_lower_close_upper_open_exit_long`

- FMZ source id: 453223 (lineage).
- Source: https://www.fmz.com/strategy/453223 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 10:39:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner lower-band dips with an upper-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `mult` [2.0, 3.0] x `atr_len` [13, 20]: **8 trials**.

## Ambiguities resolved

- The in_trade flag followed beside the position. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
