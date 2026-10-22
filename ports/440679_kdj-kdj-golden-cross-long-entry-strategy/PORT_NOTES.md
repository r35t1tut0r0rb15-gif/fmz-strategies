# #440679 KDJ阳线突破买入策略KDJ-Golden-Cross-Long-Entry-Strategy -> `fmz_440679_kdj_j_over_d_long`

- FMZ source id: 440679 (lineage).
- Source: https://www.fmz.com/strategy/440679 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 10:28:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | KDJ lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ilong` [9, 14] x `isig` [3, 5]: **4 trials**.

## Ambiguities resolved

- Date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
