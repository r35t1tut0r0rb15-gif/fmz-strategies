# #427461 5-day Moving Average Golden Cross Momentum Strategy -> `fmz_427461_ma5x_long`

- FMZ source id: 427461 (lineage).
- Source: https://www.fmz.com/strategy/427461 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 12:16:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits. |
| 2 | ADAPT | Cash profit filter (openprofit > 6000 on a 30000 unit) -> return > 20 % since the entry fill. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 2 and the cash quantities stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`l_len` [195, 100] x `multiplier` [6, 3] x `profit_gate` [0.2, 0.1]: **8 trials**; defaults 195 / 6 / 0.2 (the source's); WMA 3 / 78, ATR 40 fixed.

## Ambiguities resolved

- Two units (pyramiding 2) are sizing: one position, opened by whichever signal comes first.
- The cash profit filter becomes a return on the entry fill (the first unit's share). The 2020 start is the author's window.
- The lengths are named "2 / 5 / 10-day" averages (intraday thinking) but the header is daily: ported on daily broker-day bars. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
