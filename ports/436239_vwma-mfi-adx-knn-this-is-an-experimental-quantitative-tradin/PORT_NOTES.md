# #436239 基于VWMA和MFI-ADX的kNN机器学习量化交易策略This-is-an-experimental-quantitative-trading-strategy -> `fmz_436239_vwma13_19_cross_knn_adx_mfi_vote_reversal`

- FMZ source id: 436239 (lineage).
- Source: https://www.fmz.com/strategy/436239 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 14:13:27). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWMA crossings filtered by a kNN vote on past crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`knn` [23, 10] x `fast` [13, 8]: **4 trials**; slow 19, DMI 13 / 6, MFI 13.

## Ambiguities resolved

- kNN as coded (ties at the k-th distance included). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "machine_learning_vote"`.

## Marks

`none`
