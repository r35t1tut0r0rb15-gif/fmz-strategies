# #364527 Scalping PullBack Tool R1.1 by JustUncleL -> `fmz_364527_ha_pac_pullback`

- Source: https://www.fmz.com/strategy/364527 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-20 16:32:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

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

`pac_len` [21, 34] x `lookback` [2, 3, 5] = **6 trials**. EMA 89 / 200 stay at the originals.

## Ambiguities resolved

- Same-period Heikin-Ashi series built from the port's bars (security on timeframe.period).
- TradeDirection returning to 0 sends no order; the position is held.
- Fractals, HH/LL and EMA 600 only draw.
- `FREQ = "3min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
