# #427116 Quantitative Moving Average Trend Following Strategy -> `fmz_427116_evwma5_11_state_pct9_stop_reversal`

- FMZ source id: 427116 (lineage).
- Source: https://www.fmz.com/strategy/427116 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 13:23:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | PASS | Elastic volume-weighted average cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000, commission 0.075 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_sum_length` [5, 10] x `slow_sum_length` [11, 30]: **4 trials**; stop 9 %.

## Ambiguities resolved

- Re-entry after a stop while the condition holds, as written. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`coarse_bar_stop`
