# #426848 Medium Long Term Quantitative Trading Strategy Based on Bollinger -> `fmz_426848_bollinger_inverted_bracket`

- Source: https://www.fmz.com/strategy/426848 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 20:09:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

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

`length` [21, 51] x `mult` [2.0, 3.01] x `tp_pct` [5, 14.2]: **8 trials**, defaults 51 / 3.01 / 14.2 (the source's); stop 99 % fixed.

## Ambiguities resolved

- Kept as written: long on a fall through the upper band, short on a rise through the lower (decision owed).
- Ticks x 10 = 14.2 % / 99 % of the signal close on a 0.1 tick: ported as fractions of the fill.
- Pine population stdev. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
