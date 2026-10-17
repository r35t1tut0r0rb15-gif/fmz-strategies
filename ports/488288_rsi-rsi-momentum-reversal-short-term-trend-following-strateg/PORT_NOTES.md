# #488288 RSI动量反转短期趋势跟踪策略与移动平均线聚合-RSI-Momentum-Reversal-Short-Term-Trend-Following-Strategy-with-Moving-Average-Confluence -> `fmz_488288_rsi2_dip_sma5_exit`

- FMZ source id: 488288 (lineage).
- Source: https://www.fmz.com/strategy/488288 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 16:13:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An oscillator and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_buy` [5.0, 10.0] x `exit_ma` [5, 10]: **4 trials**; defaults 5 / 5 (the source's); RSI 2 and SMA 200 fixed.

## Ambiguities resolved

- The close tests `strategy.position_size` (the position at the bar's start): never on the entry's bar; an entry
  signal while held with the exit true closes the trade (#430850).
- The emergency stop defaults to 0 % (inert, not ported). Long only: opposite entries cannot occur. Daily bars are
  broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_mean_reversion"`.

## Marks

`none`
