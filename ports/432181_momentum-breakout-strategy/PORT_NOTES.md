# #432181 Momentum Breakout Strategy -> `fmz_432181_momentum_rising_pct_stop`

- FMZ source id: 432181 (lineage).
- Source: https://www.fmz.com/strategy/432181 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 11:09:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stops fixed at entry |
| 2 | PASS | Momentum signs and percentage stops of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [18, 9] x `sl_scale` [1.0, 0.5]: **4 trials**; the 8 % / 7 % stops are scaled together.

## Ambiguities resolved

- Stops live on the fill bar in the house engine. Re-entry after a stop as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop`
