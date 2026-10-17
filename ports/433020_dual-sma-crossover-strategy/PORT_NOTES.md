# #433020 Dual SMA Crossover Strategy -> `fmz_433020_sma_377_200_cross`

- FMZ source id: 433020 (lineage).
- Source: https://www.fmz.com/strategy/433020 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 16:42:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_a` [377, 500] x `len_b` [200, 100]: **4 trials**; buy and sell pairs equal, as the defaults.

## Ambiguities resolved

- Long on the slower average crossing above the faster one, as written. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
