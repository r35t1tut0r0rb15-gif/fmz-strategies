# #431973 Corn Moving Average Balance Trading Strategy -> `fmz_431973_ema_20_100_cross`

- FMZ source id: 431973 (lineage).
- Source: https://www.fmz.com/strategy/431973 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-13 18:00:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [20, 10] x `len2` [100, 50]: **4 trials**.

## Ambiguities resolved

- EMA types (the defaults). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
