# #427305 Moving Average Trailing Stop Strategy -> `fmz_427305_xplorr_ma_trailing`

- FMZ source id: 427305 (lineage).
- Source: https://www.fmz.com/strategy/427305 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 21:33:48). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is tested on EMA 6 of closes (signal). |
| 2 | PASS | Slopes in basis points; range multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`strength1` [52, 20] x `strength2` [100, 50] x `delta` [8, 4]: **8 trials**; defaults 52 / 100 / 8 (the source's); EMA 12 / SMA 54, EMA 18 / SMA 55, EMA 6, range 15 fixed.

## Ambiguities resolved

- The "trailing stop" compares EMA 6 of closes with a ratchet line: a close-based exit signal (rule 2), no stop and no mark.
- `atr` is the source's SMA 15 of high - low.
- Broker-day bars; testPeriod() is the constant true. Long only. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
