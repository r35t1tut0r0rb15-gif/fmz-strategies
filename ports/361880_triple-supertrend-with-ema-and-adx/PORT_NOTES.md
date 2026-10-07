# #361880 Triple-Supertrend-with-EMA-and-ADX -> `fmz_361880_triple_supertrend_agree`

- Source: https://www.fmz.com/strategy/361880 (PineScript v5, author ChaoZhang (kunjandetroja script), FMZ last
  modified 2022-05-08 21:16:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR-factor bands. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG361880` (Jaccard >= 0.80) with #427121 (DUPLICATE); best Jaccard 0.857 with #427121. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`m1` [1, 2] x `m2` [2, 3] x `m3` [3, 4] = **8 trials**. ATR lengths 10/15/20 fixed.

## Ambiguities resolved

- Re-entry is allowed (default): a fresh all-agree bar after a dir1 exit re-enters.
- The commented intraday time exit is not active.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
