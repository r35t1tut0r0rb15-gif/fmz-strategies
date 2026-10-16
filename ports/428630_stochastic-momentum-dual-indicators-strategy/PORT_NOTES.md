# #428630 Stochastic Momentum Dual Indicators Strategy -> `fmz_428630_noro_smi_rsi_2d`

- FMZ source id: 428630 (lineage).
- Source: https://www.fmz.com/strategy/428630 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-07 16:45:25). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.
- Duplicate group: **DG428630** (3 members, best partner #433007, Jaccard 0.913); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and body ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot, martingale and capital inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428630. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [50, 40] x `a` [5, 10]: **4 trials**; defaults 50 / 5 (the source's); SMI D 3, RSI 7 (20 / 80), body SMA 10 fixed.

## Ambiguities resolved

- A signal bar also meets the opposite position's exit: the entry wins (house convention).
- Martingale, capital % and switches are sizing; date window dropped. REVERSAL INTENDED.
- 2-day blocks of broker days (worker A's convention). FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
