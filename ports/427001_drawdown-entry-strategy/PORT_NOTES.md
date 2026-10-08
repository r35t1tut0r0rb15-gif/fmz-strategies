# #427001 Drawdown Entry Strategy -> `fmz_427001_noro_drawdown_long`

- Source: https://www.fmz.com/strategy/427001 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-16 19:18:38). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

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

`signal` [-3, -5, -8] %: **3 trials**, default -5 (the source's).

## Ambiguities resolved

- A qty-0 short entry is an exit (Noro's idiom); from flat the entry stands, while long the exit goes flat.
- Long only.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
