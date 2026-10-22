# #440724 RWI波动率反转策略RWI-Volatility-Contrarian-Strategy -> `fmz_440724_random_walk_index_direction`

- FMZ source id: 440724 (lineage).
- Source: https://www.fmz.com/strategy/440724 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 14:56:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Random Walk Index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 30] x `threshold` [1.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
