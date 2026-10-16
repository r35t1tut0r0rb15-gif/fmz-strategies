# #429561 双线性BB口系统策略Dual-Moving-Average-Bollinger-Band-System-Strategy -> `fmz_429561_bb_basis_cross`

- FMZ source id: 429561 (lineage).
- Source: https://www.fmz.com/strategy/429561 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-18 11:01:19). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving-average cross only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427162. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
