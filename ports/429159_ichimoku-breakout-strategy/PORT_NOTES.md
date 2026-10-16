# #429159 Ichimoku Breakout Strategy -> `fmz_429159_ichimoku_kumo_breakout`

- FMZ source id: 429159 (lineage).
- Source: https://www.fmz.com/strategy/429159 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-13 16:48:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Price vs cloud levels from the bars only. |
| 3 | PASS | "Crypto" in the title only; exchange pair in the header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429159. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ten` [18, 9] x `kij` [52, 26]: **4 trials**; Senkou B 104 and the offset 52 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
