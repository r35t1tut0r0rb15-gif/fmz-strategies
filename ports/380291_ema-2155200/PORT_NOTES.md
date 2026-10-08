# #380291 EMA 21,55,200 -> `fmz_380291_ema_21_55_200_rsi_exit`

- Source: https://www.fmz.com/strategy/380291 (PineScript v4, author Zer3192, FMZ last
  modified 2022-08-27 21:56:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() / order sizing lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG380291` (Jaccard >= 0.80) with #435952 (DUPLICATE); best Jaccard 0.850 with #435952. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 21] x `mid` [34, 55] x `slow` [100, 200] = **8 trials**. RSI 14 (70/30) stays at the original.

## Ambiguities resolved

- RSI closes are close-based exits; not applied on their own entry bar; same-side entries ignored (mirrored position).
- Fixed qty 100 -> sizing.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
