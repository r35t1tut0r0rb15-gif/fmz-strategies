# #365905 Schaff Trend Cycle -> `fmz_365905_schaff_trend_cycle`

- Source: https://www.fmz.com/strategy/365905 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-26 17:20:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

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

`fast` [12, 23] x `slow` [26, 50] x `cycle` [10, 20] = **8 trials**. %D lengths 3/3 and bands 75/25 stay at the originals.

## Ambiguities resolved

- stoch() of a flat window is na: fixnan carries the last value, nz gives 0 before any.
- Clamped to 0..100 as coded.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
