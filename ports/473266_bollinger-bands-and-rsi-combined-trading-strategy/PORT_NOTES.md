# #473266 Bollinger Bands and RSI Combined Trading Strategy -> `fmz_473266_bb20_2p5_rsi30_dip_rsi50_exit_long`

- FMZ source id: 473266 (lineage).
- Source: https://www.fmz.com/strategy/473266 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:13:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band and RSI dips with an RSI 50 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.5, 2.0] x `exit_rsi` [50, 60]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
