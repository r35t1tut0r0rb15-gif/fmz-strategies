# #426993 Parabolic SAR Trailing Stop Loss Strategy -> `fmz_426993_psar_on_close`

- Source: https://www.fmz.com/strategy/426993 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-16 18:54:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND426598` (Jaccard 0.65-0.80) with #426598 (PORT_CANDIDATE); best Jaccard 0.673 with #426598. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.01, 0.02] x `increment` [0.01, 0.02] x `maximum` [0.2]: **4 trials**, defaults 0.02 / 0.02 / 0.2 (the source's).

## Ambiguities resolved

- Bar 0 values na; the SAR starts on the second bar.
- Raw-candle version of #426489 (Heikin-Ashi) / near #426598 (ATR step).
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
