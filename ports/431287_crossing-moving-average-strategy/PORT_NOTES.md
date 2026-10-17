# #431287 Crossing Moving Average Strategy -> `fmz_431287_ema_34_89_200_crosses`

- FMZ source id: 431287 (lineage).
- Source: https://www.fmz.com/strategy/431287 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-06 17:01:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
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

`fast` [34, 20] x `mid` [89, 50]: **4 trials**; EMA 200 fixed.

## Ambiguities resolved

- Same-direction entries are one position. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
