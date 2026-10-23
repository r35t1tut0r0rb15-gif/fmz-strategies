# #488029 Multi Indicator Dynamic Trading Strategy with Volume Confirmation System -> `fmz_488029_any_bullish_trigger_volume_no_exit_1h_long_only`

- FMZ source id: 488029 (lineage).
- Source: https://www.fmz.com/strategy/488029 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 15:12:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Any of four bullish triggers on high volume |
| 3 | PASS | Exchange pair in the header only (BNB_USDT). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [1.5, 2.0] x `rsi_os` [30.0, 25.0]: **4 trials**; EMA 9 / 21, MACD 12 / 26 / 9, BB 20 x 2.

## Ambiguities resolved

- The close names a never-entered id: no exit. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "indicator_vote"`.

## Marks

`none`
