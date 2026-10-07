# #365028 QQE signals -> `fmz_365028_qqe_line_side_change`

- Source: https://www.fmz.com/strategy/365028 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-23 11:32:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365028` (Jaccard >= 0.80) with #452613 (DUPLICATE); best Jaccard 0.829 with #452613. Group `ND365028` (Jaccard 0.65-0.80) with #376314 (PORT_CANDIDATE); best Jaccard 0.718 with #376314. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [10, 14] x `sf` [5, 8] x `qqe` [3.0, 4.238] = **8 trials**.

## Ambiguities resolved

- `cross()` is either direction, as in Pine v4.
- `qqeLong` needs `FastAtrRsiTL[1] - 50` non-zero and defined (Pine float-as-bool).
- "Thresh-hold" is declared but unused.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
