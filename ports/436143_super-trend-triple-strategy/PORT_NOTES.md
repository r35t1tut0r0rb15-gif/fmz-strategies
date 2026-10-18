# #436143 Super Trend Triple Strategy -> `fmz_436143_triple_supertrend_swapped_args`

- FMZ source id: 436143 (lineage).
- Source: https://www.fmz.com/strategy/436143 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 16:02:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend lines and an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [100, 200] x `factor_scale` [1.0, 2.0]: **4 trials**; ATR lengths 12 / 11 / 10 and factors 3 / 2 / 1 (scaled) as written.

## Ambiguities resolved

- Supertrend arguments swapped as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
