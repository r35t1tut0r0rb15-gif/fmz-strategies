# #446526 Dynamic Trend Following Strategy -> `fmz_446526_close_sma5_sma20_double_cross_pct_bracket_reversal`

- FMZ source id: 446526 (lineage).
- Source: https://www.fmz.com/strategy/446526 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 11:38:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; brackets fixed at entry (re-sent levels marked) |
| 2 | PASS | Double SMA crossings with percent brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The portfolio share and leverage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [20, 50] x `sl` [0.02, 0.01]: **4 trials**; the take-profit fractions and the SMA 5 fixed.

## Ambiguities resolved

- Percent brackets from the fill; repeat-signal moves not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
