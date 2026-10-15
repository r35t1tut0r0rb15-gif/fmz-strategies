# #427301 Percent Trailing Stop Loss Strategy -> `fmz_427301_sma_cross_pct_trail`

- FMZ source id: 427301 (lineage).
- Source: https://www.fmz.com/strategy/427301 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 21:18:39). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; trailing stop pending (mark). |
| 2 | PASS | MA lengths, percent trail. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Trailing stop quoted in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 40, 80]: **6 trials**; defaults 10 / 20 (the source's). `trail_pct` 10 is recorded for the pending trail.

## Trailing stop (rule 2, mark `trailing_stop_pending`)

As written: long `stop = max(close x (1 - 10 %), stop[1])`, short `stop = min(close x (1 + 10 %), stop[1])`, computed on each **2-hour** bar close and placed as a stop order for the next bar. The house trail (`stops()["trail"]`, type percent, anchor close) ratchets on the best **minute** close up to the previous minute, so on 2-hour bars it would trail tighter than the source. Not expressible exactly: kept pending, not emitted. (On 1-minute bars the same code is expressible: see #427266.)

## Ambiguities resolved

- REVERSAL INTENDED (the crosses reverse). FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
