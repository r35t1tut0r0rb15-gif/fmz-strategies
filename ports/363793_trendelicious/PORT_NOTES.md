# #363793 Trendelicious -> `fmz_363793_trendelicious_midline_trend`

- Source: https://www.fmz.com/strategy/363793 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-17 13:47:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

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

`length` [20, 30, 50] = **3 trials**.

## Ambiguities resolved

- Aggressive mode (default false) not ported.
- `uptrend` starts false, so the script is short from its first bar until the first up-trend; kept.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
