# #427122 T7-JNSAR Quantitative Trading Strategy -> `fmz_427122_t7_jnsar`

- FMZ source id: 427122 (lineage).
- Source: https://www.fmz.com/strategy/427122 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 14:05:19). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | `round()` to a whole price unit dropped (instrument-specific). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [5, 3, 10] x `lags` [5, 3]: **6 trials**; defaults 5 / 5 (the source's: EMA 5 over the current and 4 previous bars).

## Ambiguities resolved

- `round(sum / 15)` -> `sum / 15` (criterion 2).
- Always in the market (REVERSAL INTENDED).
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
