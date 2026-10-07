# #362842 SSS -> `fmz_362842_sss_ssl_flip_long_tp`

- Source: https://www.fmz.com/strategy/362842 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 12:30:11). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Commented-out strategy() sizing only (inactive) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG362842` (Jaccard >= 0.80) with #435866 (DUPLICATE); best Jaccard 0.821 with #435866. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [50, 100, 200] x `take_profit` [0.5, 1.0, 2.0] % = **9 trials**. SSL length 200 and the candle EMAs (25/20) stay at the originals.

## Ambiguities resolved

- Take-profit at entry +1 % -> `tp_stop` fraction in stops(), shifted one bar.
- `close < MA -> strategy.exit(stop = close)` is a close-based stop: exit signal on that close (rule 3).
- Entries need a flat position; simulate() mirrors the engine take-profit. Long only (`upon_opposite_entry="ignore"`).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
