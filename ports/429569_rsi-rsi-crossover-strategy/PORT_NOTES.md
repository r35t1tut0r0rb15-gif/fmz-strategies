# #429569 RSI金叉死叉策略RSI-Crossover-Strategy -> `fmz_429569_rsi_ema_cross_state`

- FMZ source id: 429569 (lineage).
- Source: https://www.fmz.com/strategy/429569 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 11:44:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI averages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 30]: **4 trials**; RSI 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
