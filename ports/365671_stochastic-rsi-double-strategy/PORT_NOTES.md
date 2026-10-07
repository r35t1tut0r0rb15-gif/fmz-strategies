# #365671 Stochastic + RSI, Double Strategy (by ChartArt) -> `fmz_365671_stoch_rsi_double_cross`

- Source: https://www.fmz.com/strategy/365671 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-25 16:12:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365671` (Jaccard >= 0.80) with #436762 (DUPLICATE); best Jaccard 1.000 with #436762. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [9, 14] x `rsi_len` [7, 14] x `smooth` [3, 5] (both %K and %D) = **8 trials**. Levels 80/20 and 70/30 stay at the originals.

## Ambiguities resolved

- Both crosses on the same bar, as coded.
- No exits: entries reverse.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`none`
