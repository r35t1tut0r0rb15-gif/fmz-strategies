# #356844 MACD-pine -> `fmz_356844_macd_signal_cross_reverse`

- Source: https://www.fmz.com/strategy/356844 (PineScript, FMZ last modified 2022-05-23 18:08:17).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS | MACD cross only. |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | No sizing code (Pine defaults). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`fast` [8, 12, 16] x `slow` [21, 26, 34] = **9 trials**. Signal 9 fixed.

## Ambiguities resolved

- No `strategy()` call in the source (FMZ defaults: pyramiding 0, market orders at the next open).
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
