# #426856 Quantitative Strategy Combining Mean Reversion and Trend Following -> `fmz_426856_mean_reversion_trend_long`

- Source: https://www.fmz.com/strategy/426856 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 20:45:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`sma_len` [100, 200] x `rsi_buy` [10, 20] x `rsi_close` [70, 80]: **8 trials**, defaults 200 / 20 / 80 (the source's).

## Ambiguities resolved

- The limit-at-close exit is ported as a close-based exit filled next open (decision owed).
- Origin set at the signal bar; position factor is sizing.
- Long only. Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
