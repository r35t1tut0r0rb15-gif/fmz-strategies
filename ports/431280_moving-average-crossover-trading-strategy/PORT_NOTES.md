# #431280 Moving Average Crossover Trading Strategy -> `fmz_431280_hlc3_ema_cross_long`

- FMZ source id: 431280 (lineage).
- Source: https://www.fmz.com/strategy/431280 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 16:38:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_len` [48, 100] x `exit_len` [30, 15]: **4 trials**; EMA 13 fixed.

## Ambiguities resolved

- EMA type (the default). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
