# #439875 动态双EMA游离停止策略Dynamic-Dual-EMA-Trailing-Stop-Strategy -> `fmz_439875_ema60_90_macd_trend_reversal`

- FMZ source id: 439875 (lineage).
- Source: https://www.fmz.com/strategy/439875 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 15:13:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stack and MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema60_period` [60, 30] x `ema90_period` [90, 120]: **4 trials**; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Exits that can never fire, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
