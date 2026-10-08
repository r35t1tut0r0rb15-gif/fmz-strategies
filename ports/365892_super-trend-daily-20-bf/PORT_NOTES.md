# #365892 Super Trend Daily 2.0 BF -> `fmz_365892_dual_supertrend_roc_filter`

- Source: https://www.fmz.com/strategy/365892 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-26 16:48:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365892` (Jaccard >= 0.80) with #426602 (DUPLICATE); best Jaccard 0.922 with #426602. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len_l` [15, 30] x `roc_len_s` [38, 76] x `sl_long` [0.03, 0.05] = **8 trials**. SuperTrends 2 x 1.5 / 3 x 1.3, ROC 6 % and the 6 % short stop stay at the originals.

## Ambiguities resolved

- Fixed 5 % / 6 % stops on the entry price -> `sl_stop` fractions per side, shifted one bar; the source activates them one bar after the fill.
- Same-bar long and short: the later order (short) wins.
- v4 integer division: ROC EMA 15 / 38. testPeriod() is true.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
