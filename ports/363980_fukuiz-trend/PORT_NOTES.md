# #363980 Fukuiz Trend -> `fmz_363980_rsi_regular_divergence`

- Source: https://www.fmz.com/strategy/363980 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-18 10:51:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 24] x `lb` (left = right) [3, 5, 8] = **6 trials**. Range 5..60 stays at the original.

## Ambiguities resolved

- RSI on open (source default). Pivots confirmed 5 bars later; `valuewhen(found, x, 1)` = previous found pivot.
- RSI 24 / 100 trend colours only draw.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
