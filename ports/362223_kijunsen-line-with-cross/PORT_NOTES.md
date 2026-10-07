# #362223 KijunSen-Line-With-Cross -> `fmz_362223_hl2_kijun_cross`

- Source: https://www.fmz.com/strategy/362223 (PineScript v5, author ChaoZhang (dilan1999 indicator), FMZ last
  modified 2022-05-10 18:56:36). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Range midpoint only. |
| 3 | PASS | No venue code. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [9, 26, 52] = **3 trials**.

## Ambiguities resolved

- No backtest header: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`bar_size_pending`
