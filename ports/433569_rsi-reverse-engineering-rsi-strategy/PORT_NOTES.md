# #433569 逆向工程RSI策略Reverse-Engineering-RSI-Strategy -> `fmz_433569_reverse_engineered_rsi`

- FMZ source id: 433569 (lineage).
- Source: https://www.fmz.com/strategy/433569 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-28 15:50:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The close against an RSI-derived price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`value` [50, 60] x `wild_per` [14, 28]: **4 trials**.

## Ambiguities resolved

- Averages seeded with 1 as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
