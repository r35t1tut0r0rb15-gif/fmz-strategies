# #437400 动量均线交叉和MACD过滤的海肯阿什蜡烛策略Momentum-Crossover-Moving-Average-and-MACD-Filter-Heikin-Ashi-Candlestick-Strategy -> `fmz_437400_intraday_ha_close_ema_cross`

- FMZ source id: 437400 (lineage).
- Source: https://www.fmz.com/strategy/437400 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-02 12:18:03). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; intraday values end with the daily bar |
| 2 | PASS | Average crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430040. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fama` [16, 10] x `sloma` [21, 30]: **4 trials**; the 15 / 300-minute frames fixed; MACD filter off.

## Ambiguities resolved

- Intraday frames = the day's last 15 / 300-minute bars from the broker day's start; MACD filter off. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
