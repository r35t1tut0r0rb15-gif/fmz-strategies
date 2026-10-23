# #488295 多指标MACD动量期权策略与风险控制百分比退出机制-Multi-Indicator-MACD-Momentum-Options-Strategy-with-Risk-Controlled-Percentage-Based-Exits -> `fmz_488295_sharp_macd_cross_sma50_volume_bracket_1h_reversal`

- FMZ source id: 488295 (lineage).
- Source: https://www.fmz.com/strategy/488295 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 16:46:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 1 % / 2 % bracket from the fill (longs), one-bar shorts |
| 2 | PASS | Sharp MACD crossings in the SMA 50 trend on volume |
| 3 | PASS | Exchange pair in the header only (SPY / Tesla / Apple named in the comments). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sharp` [1.0, 5.0] x `sl` [0.01, 0.02]: **4 trials**; MACD 12 / 26 / 9, SMA 50, RSI 14, TP 2 %.

## Ambiguities resolved

- Shorts close one bar after the fill (long-side levels). Bracket from the fill for longs. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
