# #440461 Squeeze Momentum Breakout Strategy -> `fmz_440461_squeeze_release_momentum_fade_exit_1h_long_only`

- FMZ source id: 440461 (lineage).
- Source: https://www.fmz.com/strategy/440461 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 17:33:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Squeeze release with positive momentum, closed when momentum fades |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x leverage / close x risk %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [21, 20] x `kc_mult` [1.5, 2.0]: **4 trials**; KC 20, true range.

## Ambiguities resolved

- BB deviation uses the KC factor as written; VWMA filter off. Volume not used. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "squeeze_momentum"`.

## Marks

`none`
