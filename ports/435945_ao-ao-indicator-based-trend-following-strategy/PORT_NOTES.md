# #435945 基于AO指标和均线的趋势跟踪策略AO-Indicator-Based-Trend-Following-Strategy -> `fmz_435945_ao_ema_trend_percent_bracket`

- FMZ source id: 435945 (lineage).
- Source: https://www.fmz.com/strategy/435945 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 11:59:48). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Percent bracket and standard indicators |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The profit and stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`profit` [10.0, 5.0] x `stop` [5.0, 2.0]: **4 trials** (percent, as the author's inputs); AO 5 / 34, RSI 7 and EMA 20 / 200 fixed.

## Ambiguities resolved

- Per-side percent bracket from the author's formulas; levels fixed at the fill. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
