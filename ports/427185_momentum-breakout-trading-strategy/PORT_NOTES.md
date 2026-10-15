# #427185 Momentum Breakout Trading Strategy -> `fmz_427185_noro_bands_scalper_v16`

- FMZ source id: 427185 (lineage).
- Source: https://www.fmz.com/strategy/427185 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 21:28:22). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.
- Near-duplicate group: **DG427185** (with #439225, Jaccard 0.858); ported anyway (rule 7). Related
  in idea (no group) to worker A's #426995 (Noro bands scalper, older version); same reading of the
  qty-0 idiom.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts and ratios of averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per trade stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427185. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40] x `bodylen` [10, 15]: **6 trials**; defaults 20 / 10 (the source's); take 0 %, trend bars 1, bands entry on fixed.

## Ambiguities resolved

- Counter-trend entries (qty 0) only close the opposite position; the entry price is the next open after the signal.
- The 1900-2100 window and the close_all after it are the author's backtest window: dropped.
- REVERSAL INTENDED. FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
