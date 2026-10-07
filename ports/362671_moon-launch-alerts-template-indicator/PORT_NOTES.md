# #362671 ML Alerts Template [indicator] -> `fmz_362671_moon_launch_state_machine`

- Source: https://www.fmz.com/strategy/362671 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 18:45:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG362671` (Jaccard >= 0.80) with #363756 (DUPLICATE); best Jaccard 0.970 with #363756. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [10, 20] x `atr_len` [12, 24] = **4 trials**. MACD 12/26/9 stays at the original.

## Ambiguities resolved

- `prev5` is re-declared 0 each bar, so its fallback is 0; the latches use `[1]` and carry state.
- "Trade Shorts"/"Trade Exits" default true; GoExit is an alert only (no order).
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
