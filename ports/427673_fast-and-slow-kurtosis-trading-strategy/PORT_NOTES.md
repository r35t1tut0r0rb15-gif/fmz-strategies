# #427673 Fast and Slow Kurtosis Trading Strategy -> `fmz_427673_hpotter_fast_slow_kurtosis`

- FMZ source id: 427673 (lineage).
- Source: https://www.fmz.com/strategy/427673 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-23 15:27:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Momentum of closes, zero level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_len` [3, 5] x `ema_len` [65, 30]: **4 trials**; defaults 3 / 65 (the source's); WMA 3 and BuyZone 0 fixed.

## Ambiguities resolved

- "Trade reverse" fixed off. pos is -1 while the averages are na (as written).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
