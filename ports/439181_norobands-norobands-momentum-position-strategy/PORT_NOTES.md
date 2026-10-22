# #439181 动量位置型NoroBands波段策略NoroBands-Momentum-Position-Strategy -> `fmz_439181_noro_bands_v15`

- FMZ source id: 439181 (lineage).
- Source: https://www.fmz.com/strategy/439181 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-18 10:58:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel distance bands, bar colours, a fast RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; pyramiding clauses stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [20, 40] x `use_cb` [True, False]: **4 trials**; the other filters on.

## Ambiguities resolved

- Adds blocked; short wins a both-setup bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
