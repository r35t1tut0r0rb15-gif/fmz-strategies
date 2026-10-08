# #365907 SMA call buy/sale (SWING CALLS) -> `fmz_365907_ema_sma_swing_cross`

- Source: https://www.fmz.com/strategy/365907 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-26 17:28:12). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

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

`ema_len` [5, 10] x `sma_len` [20, 50, 100] = **6 trials**.

## Ambiguities resolved

- RSI 80/20 reversal markers only draw.
- Long needs high > SMA, short needs a down bar, as coded.
- `FREQ = "1min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
