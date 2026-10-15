# #427064 RSI-W Pattern Breakout Strategy -> `fmz_427064_rsi_w_pattern_long`

- FMZ source id: 427064 (lineage).
- Source: https://www.fmz.com/strategy/427064 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-17 18:24:17). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 8 % stop is a close test (exit signal). |
| 2 | PASS | RSI levels, EMA lengths, stop as a fraction of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | pyramiding = 2 adds stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [5, 7] x `buy_rsi_entry` [65, 55] x `stop_pct` [8, 5]: **8 trials**; defaults 5 / 65 / 8 (the source's); EMA 50 / 20 and the RSI 75 exit fixed.

## Ambiguities resolved

- Adds (pyramiding 2) are sizing; entries only from flat, so the average price is the entry fill (next open).
- The "SL Exit" is `close < avg x 0.92` on the completed bar: an exit signal (rule 3).
- One signal per bar; an exit never on the bar that signalled the entry.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
