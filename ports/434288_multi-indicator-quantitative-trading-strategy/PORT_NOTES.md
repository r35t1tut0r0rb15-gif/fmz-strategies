# #434288 Multi Indicator Quantitative Trading Strategy -> `fmz_434288_sma_50_100_state_long`

- FMZ source id: 434288 (lineage).
- Source: https://www.fmz.com/strategy/434288 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 10:29:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily value from completed broker days |
| 2 | PASS | Moving-average order and RSI bounds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [50, 20] x `len2` [100, 200]: **4 trials**; RSI 20 bounds 0 / 100 fixed.

## Ambiguities resolved

- Defaults only; the RSI gate always passes once defined. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
