# #442403 Three RSI Moving Average Bands Strategy -> `fmz_442403_three_rsi_ribbon_colour_reversal`

- FMZ source id: 442403 (lineage).
- Source: https://www.fmz.com/strategy/442403 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 16:18:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI ribbon colour agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_norm` [75, 50] x `rsi_slow` [100, 150]: **4 trials**; RSI fast 50 and the ribbon lengths fixed.

## Ambiguities resolved

- Colour helpers and cross-block references as written; the exit enters short. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
