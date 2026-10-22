# #439989 Dual Indicators Breakthrough Strategy -> `fmz_439989_hobbiecode_rsi2_prior_high_exit_long`

- FMZ source id: 439989 (lineage).
- Source: https://www.fmz.com/strategy/439989 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:39:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level and a prior-high break |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [2, 3] x `rsi_lower` [15, 10]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
