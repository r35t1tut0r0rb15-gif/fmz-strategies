# #430876 Heiken Ashi and Super Trend Strategy -> `fmz_430876_heikin_ashi_supertrend_tp`

- FMZ source id: 430876 (lineage).
- Source: https://www.fmz.com/strategy/430876 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 16:15:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target fixed at entry |
| 2 | PASS | A Heikin Ashi SuperTrend and a percentage target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430876. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `tp_pct` [1.1, 3.0]: **4 trials**; ATR 10 fixed.

## Ambiguities resolved

- Target distance from close[1] of the signal bar, re-based on the fill. Mark coarse_bar_stop. REVERSAL INTENDED.
  FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
