# #435704 基于SMA和PSAR指标的多空策略SMA-and-PSAR-Strategy-for-Spot-Trading -> `fmz_435704_sma_psar_reversal`

- FMZ source id: 435704 (lineage).
- Source: https://www.fmz.com/strategy/435704 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 10:31:31). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | The time exit is never true: no exit as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [1000, 500] x `psar_start` [0.02, 0.01]: **4 trials**; increment 0.01 and maximum 0.2 fixed.

## Ambiguities resolved

- Time exit never true: no exit. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
