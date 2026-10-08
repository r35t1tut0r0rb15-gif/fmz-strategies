# #426489 PSAR Heikin Ashi PSAR Trend Trading Strategy -> `fmz_426489_heikin_ashi_psar`

- Source: https://www.fmz.com/strategy/426489 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 15:16:17). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.01, 0.02] x `increment` [0.01, 0.02] x `maximum` [0.2]: **4 trials**, defaults 0.02 / 0.02 / 0.2 (the source's).

## Ambiguities resolved

- As written, the short side's acceleration test reads the raw low, not halow.
- Bar 0 values are na; the SAR starts on the second bar (barstate.isfirst[1]).
- Date window dropped.
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
