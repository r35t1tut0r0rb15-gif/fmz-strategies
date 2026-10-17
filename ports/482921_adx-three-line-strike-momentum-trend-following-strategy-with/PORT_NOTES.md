# #482921 三线突破动量趋势跟踪策略结合ADX过滤器-Three-Line-Strike-Momentum-Trend-Following-Strategy-with-ADX-Filter -> `fmz_482921_three_line_strike_adx_atr_bracket`

- FMZ source id: 482921 (lineage).
- Source: https://www.fmz.com/strategy/482921 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 17:46:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Candle colours and bodies, ADX and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG482921 (2 members, best partner #483019, Jaccard 1.000). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25.0, 20.0] x `tp_mult` [2.0, 3.0]: **4 trials**; defaults 25 / 2 (the source's); ATR 14, ADX 14
and the 1 ATR stop fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar. The port keeps the entry's bracket.

## Ambiguities resolved

- The ADX is the source's own (its -DM uses the rise of the low), as written; `ta.tr(true)` on the first bar.
- #483019 is this source's duplicate (DG482921, already marked DUPLICATE in screening).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick"`.

## Marks

`trailing_stop_pending`
