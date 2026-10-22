# #439977 动量张弛指标与123形态策略Momentum-Oscillator-123-Pattern-Strategy -> `fmz_439977_reversal123_dynamic_period_rsi_combo`

- FMZ source id: 439977 (lineage).
- Source: https://www.fmz.com/strategy/439977 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 14:27:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit volatility period -> BTC-scale reading |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `scale` [42000.0, 4200.0]: **4 trials**; the DMI zones and limits fixed.

## Ambiguities resolved

- Volatility period read on a BTC scale; RSI of the period series as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
