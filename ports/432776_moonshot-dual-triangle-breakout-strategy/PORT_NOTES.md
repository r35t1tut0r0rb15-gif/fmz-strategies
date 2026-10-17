# #432776 Moonshot Dual Triangle Breakout Strategy -> `fmz_432776_triple_supertrend_ema`

- FMZ source id: 432776 (lineage).
- Source: https://www.fmz.com/strategy/432776 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 13:49:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | SuperTrend states, an EMA and a percentage stop of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the stops quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [233, 100] x `sl_pct` [1.0, 2.0]: **4 trials**; the three SuperTrends fixed.

## Ambiguities resolved

- "and" before "or" as written. Closes act on the bar-start position. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
