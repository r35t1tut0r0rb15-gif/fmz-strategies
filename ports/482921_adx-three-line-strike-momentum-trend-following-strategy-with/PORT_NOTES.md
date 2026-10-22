# #482921 三线突破动量趋势跟踪策略结合ADX过滤器-Three-Line-Strike-Momentum-Trend-Following-Strategy-with-ADX-Filter -> `fmz_482921_three_line_strike_adx25_atr_1_2_bracket_reversal`

- FMZ source id: 482921 (lineage).
- Source: https://www.fmz.com/strategy/482921 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 17:46:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Three-line-strike candles with an ADX filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG482921. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25.0, 20.0] x `tp_atr` [2.0, 3.0]: **4 trials**; ATR 14, ADX 14, stop 1 ATR.

## Ambiguities resolved

- The hand-built ADX (minusDM from a rising low) is kept as written. A repeat signal's re-sent bracket is pending.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
