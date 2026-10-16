# #429782 Moving Average Tracking Strategy -> `fmz_429782_sma200_side_change`

- FMZ source id: 429782 (lineage).
- Source: https://www.fmz.com/strategy/429782 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 17:03:32). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A price-vs-average side. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100]: **2 trials**.

## Ambiguities resolved

- Inert exits. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
