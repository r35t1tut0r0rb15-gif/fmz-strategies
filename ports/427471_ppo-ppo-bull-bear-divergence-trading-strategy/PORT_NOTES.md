# #427471 PPO Bull Bear Divergence Trading Strategy -> `fmz_427471_ppo_divergence`

- FMZ source id: 427471 (lineage).
- Source: https://www.fmz.com/strategy/427471 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 15:16:50). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; extremes only once confirmed (bar [1] against the current bar). |
| 2 | PASS | Percentage oscillator, comparisons of the instrument's own prices. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [55, 30] x `fast` [12, 8] x `long_term_div` [True, False]: **8 trials**; defaults 55 / 12 / True (the source's); slow 26, smoother 2 fixed.

## Ambiguities resolved

- Every valuewhen / barssince / lowest / highest chain is reproduced as written (occurrence 0 = latest event; comparisons with na false; `low[1] and ...` as a boolean).
- The PPO is of the OPEN (the source's `source = open`).
- PPO tops close longs, bottoms close shorts; entries win over same-bar closes (REVERSAL INTENDED). Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`none`
