# #436133 Ichimoku云图量化交易策略A-Quantitative-Ichimoku-Cloud-Trading-Strategy -> `fmz_436133_ichimoku_cloud_cross_combos`

- FMZ source id: 436133 (lineage).
- Source: https://www.fmz.com/strategy/436133 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-21 15:33:05). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cloud crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash order size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 7] x `displacement` [26, 20]: **4 trials**; base 26 and span B 52 fixed.

## Ambiguities resolved

- Displaced spans read from the past; one cross event with two lines beyond the cloud. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
