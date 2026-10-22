# #473410 Dynamic Signal Line Trend Following and Volatility Filtering Strategy -> `fmz_473410_dsl_lines_beluga_osc_band_stop_rr_from_flat`

- FMZ source id: 473410 (lineage).
- Source: https://www.fmz.com/strategy/473410 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 17:02:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | DSL trend lines with an oscillator trigger and an R-multiple bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Slippage stored, not ported; daily goal off. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 50] x `offset` [30, 15] x `risk_reward` [1.5, 2.0]: **8 trials**; band width 1, Beluga 10, Fast mode.

## Ambiguities resolved

- Daily goal off (default). Entries only from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
