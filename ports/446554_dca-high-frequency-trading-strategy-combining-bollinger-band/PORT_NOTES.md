# #446554 布林带与DCA结合的高频交易策略-High-Frequency-Trading-Strategy-Combining-Bollinger-Bands-and-DCA -> `fmz_446554_lower_band_counted_buy_upper_exit_long`

- FMZ source id: 446554 (lineage).
- Source: https://www.fmz.com/strategy/446554 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:20:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lower-band closes counted by the script, upper-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The DCA quantities stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `mult` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Add-on buys never fill (no pyramiding); counter as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
