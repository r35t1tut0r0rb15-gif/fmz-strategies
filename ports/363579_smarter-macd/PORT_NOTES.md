# #363579 Smarter MACD -> `fmz_363579_macd_rising_bottoms`

- Source: https://www.fmz.com/strategy/363579 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-16 17:05:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

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

`fast` [8, 12] x `slow` [26, 34] x `signal` [9, 23] = **8 trials**.

## Ambiguities resolved

- Bottom/top latches start at 0 (barstate.isfirst) and change only on histogram zero crosses.
- Average lines and the table only draw.
- `FREQ = "3min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
