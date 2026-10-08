# #426774 Moving Average Percentage Reversal Strategy -> `fmz_426774_ma_percent_distance`

- Source: https://www.fmz.com/strategy/426774 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 14:53:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A24). Not run.

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

`length` [14, 28] x `sell_zone` [0.54, 1.0] x `buy_zone` [0.03, 0.1]: **8 trials**, defaults 14 / 0.54 / 0.03 (the source's).

## Ambiguities resolved

- Absolute distance: "short" also fires far above the SMA, as written.
- "Trade reverse" off.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks (2026-10-07)

`none`
