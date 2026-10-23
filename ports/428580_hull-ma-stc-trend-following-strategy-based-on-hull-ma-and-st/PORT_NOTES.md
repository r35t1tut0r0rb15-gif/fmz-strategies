# #428580 基于Hull-MA与STC指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Hull-MA-and-STC-Indicator -> `fmz_428580_ut_bot_stc_hull55_agreement_close_stop_reversal`

- FMZ source id: 428580 (lineage).
- Source: https://www.fmz.com/strategy/428580 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-07 10:20:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop; target from the fill |
| 2 | PASS | ATR trailing state with Schaff cycle and Hull trend agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [2.0, 1.0] x `hull_len` [55, 100]: **4 trials**; ATR 6, STC 80 / 27 / 50, SL 15 %.

## Ambiguities resolved

- Template exits as written. Volume only in alerts. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
