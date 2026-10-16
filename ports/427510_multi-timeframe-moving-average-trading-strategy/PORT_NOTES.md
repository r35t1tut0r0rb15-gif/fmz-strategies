# #427510 Multi-Timeframe Moving Average Trading Strategy -> `fmz_427510_cm_ultimate_ma_weekly`

- FMZ source id: 427510 (lineage).
- Source: https://www.fmz.com/strategy/427510 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 20:45:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.
- Near-duplicate group: **ND427510** (3 members, best partner #438047, Jaccard 0.764); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the security call reads the chart's own period. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427510. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40] x `ma_type` [1 SMA, 2 EMA]: **6 trials**; defaults 20 / SMA (the source's); colour smoothing 2 fixed.

## Ambiguities resolved

- "Use Current Chart Resolution" on: no other timeframe is read. VWMA (type 5) excluded (volume).
- The level-less strategy.exit calls never act. REVERSAL INTENDED.
- Weekly bars as worker A's 7-day ports (`FREQ = "1W"`, weeks of broker-day dates).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
