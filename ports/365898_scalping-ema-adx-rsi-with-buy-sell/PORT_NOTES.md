# #365898 EMA RSI ADX Scalping Alerts -> `fmz_365898_ema_rsi_adx_scalper`

- Source: https://www.fmz.com/strategy/365898 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-26 17:11:01). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`ema_len` [20, 50, 100] x `rsi_len` [3, 5] x `adx_limit` [25, 30] = **12 trials**. RSI levels 80/20 and ADX 5/5 stay at the originals.

## Ambiguities resolved

- MA type default EMA; MA rule on by default.
- ADX as Pine dirmov/adx (RMA, fixnan on DI).
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
