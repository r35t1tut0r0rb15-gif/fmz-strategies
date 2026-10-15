# #427065 Dual Stochastic Oscillator Strategy -> `fmz_427065_double_stochastic`

- FMZ source id: 427065 (lineage).
- Source: https://www.fmz.com/strategy/427065 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-17 18:26:16). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; `security` on the chart's own period. |
| 2 | PASS | Oscillator levels; exits at a price ratio (1.2) of an earlier signal close. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_k` [5, 9] x `slow_k` [97, 60] x `exit_factor` [1.2, 1.05]: **8 trials**; defaults 5 / 97 / 1.2 (the source's); smoothing 2 and 1 fixed.

## Ambiguities resolved

- `valuewhen(buy == 1, close, 1)` = the close of the second most recent buy bar (Pine's occurrence 1); the exit level refers to the previous signal, not the entry. Ported as written.
- `ema(x, 1)` is x; the "Lagging D" input is never used by the script.
- Reversals in one bar (REVERSAL INTENDED); the opposite entry wins over a same-bar close.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
