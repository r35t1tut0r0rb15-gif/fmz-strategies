# #481364 Momentum Driven Keltner Channel Breakout Trading Strategy -> `fmz_481364_keltner20_breakout_momentum14_reversal`

- FMZ source id: 481364 (lineage).
- Source: https://www.fmz.com/strategy/481364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 15:03:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner breakouts with momentum confirmation and exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_kc` [20, 50] x `mult` [1.5, 2.5]: **4 trials**; momentum 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`none`
