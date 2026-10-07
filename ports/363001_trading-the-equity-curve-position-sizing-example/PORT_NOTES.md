# #363001 Trading the Equity Curve Position Sizing Example -> `fmz_363001_cmo_cross_mom_supertrend`

- Source: https://www.fmz.com/strategy/363001 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 22:30:27). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Equity-curve position sizing (lines 76-108) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG363001` (Jaccard >= 0.80) with #438939 (DUPLICATE); best Jaccard 0.876 with #438939. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmo_len` [9, 14] x `st_factor` [2.0, 3.0] x `mom_len` [12, 24] = **8 trials**. CMO signal 10 and SuperTrend ATR 10 stay at the originals.

## Ambiguities resolved

- The equity-curve logic only sets the quantity -> `original_sizing.txt`; Adj* and Def* entries have the same rules.
- `close > stupind` is false when the SuperTrend is down (na), and vice versa.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
