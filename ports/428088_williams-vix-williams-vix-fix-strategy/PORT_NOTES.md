# #428088 Williams VIX Fix Strategy -> `fmz_428088_williams_vix_fix_long`

- FMZ source id: 428088 (lineage).
- Source: https://www.fmz.com/strategy/428088 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:29:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.
- Duplicate group: **DG428088** (3 members, best partner #428627, Jaccard 0.981); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Percent distances, bands, stochastic levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 9 and equity quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428088. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd` [22, 11] x `ph` [0.85, 0.9]: **4 trials**; defaults 22 / 0.85 (the source's); BB 20 x 2, percentile look-back 50, strength 3, LB 14 / 40, stochastic 14 / 3 / 3 / 80 fixed.

## Ambiguities resolved

- Adds (pyramiding 9) are sizing. A same-bar entry and close while long: the close wins (stated). RSI unused. Long only.
- Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`none`
