# #426598 ATR Parabolic SAR Trailing Stop Strategy Based on ATR Indicator -> `fmz_426598_atr_parabolic_sar`

- Source: https://www.fmz.com/strategy/426598 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-13 15:53:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426598` (Jaccard 0.65-0.80) with #426993 (PORT_CANDIDATE); best Jaccard 0.673 with #426993. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.01, 0.02] x `increment` [0.01, 0.02] x `entry_bars` [1, 2]: **8 trials**, defaults 0.02 / 0.02 / 1 (the source's); ATR 14 and max 0.2 fixed.

## Ambiguities resolved

- The SAR steps by af x ATR (not toward the extreme point), as written.
- Bar 0 values are na; the SAR starts on bar 1, where trend_bars can already reach +-1.
- tr is na on the first bar, then fills the ATR warm-up.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
