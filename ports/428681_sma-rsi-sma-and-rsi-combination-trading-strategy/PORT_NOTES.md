# #428681 SMA and RSI Combination Trading Strategy -> `fmz_428681_alpha_short_sma_rsi`

- FMZ source id: 428681 (lineage).
- Source: https://www.fmz.com/strategy/428681 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-08 11:40:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18) AS WRITTEN. Not run.
- Duplicate group: **DG428681** (2 members, best partner #428682, Jaccard 0.901); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and MA length. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428681. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_entry` [51, 60] x `sma_length` [200, 100]: **4 trials**; defaults 51 / 200 (the source's); RSI 14, exits 54 / 32 fixed.

## Ambiguities resolved

- The "trailing stop" is the lowest close since entry: the short closes on the first close that is not a new low (close-checked), as written.
- strategy() commented out. Short only. 2-day blocks of broker days (worker A's convention); FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
