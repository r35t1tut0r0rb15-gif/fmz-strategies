# #380251 EMA SCALPEUR -> `fmz_380251_ema_cross_short_only`

- Source: https://www.fmz.com/strategy/380251 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-27 17:17:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() / order sizing lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG380251` (Jaccard >= 0.80) with #426802 (DUPLICATE); best Jaccard 1.000 with #426802. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_l` [9, 12] x `ema_l2` [21, 26] x `rsi_len` [5, 14] = **8 trials**. EMA 100 / 55 exit pair stays at the original.

## Ambiguities resolved

- Short only, as written (rule 6); upon_opposite_entry="ignore".
- A close on its own entry bar does not apply; entries while short are ignored.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
