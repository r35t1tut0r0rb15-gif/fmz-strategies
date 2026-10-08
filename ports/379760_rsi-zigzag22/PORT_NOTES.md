# #379760 RSI -ZIGZAG -> `fmz_379760_rsi_cross_zigzag`

- Source: https://www.fmz.com/strategy/379760 (PineScript v4, author Zer3192, FMZ last
  modified 2022-08-24 04:08:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND379760` (Jaccard 0.65-0.80) with #442536 (PORT_CANDIDATE); best Jaccard 0.701 with #442536. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [1, 2, 3] x `zz_pct` [0.5, 1.0, 2.0] = **9 trials**. RSI levels 35/70 stay at the originals.

## Ambiguities resolved

- RSI length 1 (input default): 100 up / 0 down / 100 flat (Pine rsi()), kept as written.
- HH/LL start at the first bar (0 before any cross); trend starts 1.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
