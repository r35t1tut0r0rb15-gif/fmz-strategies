# #442946 Awesome Oscillator Double Stochastic Filtered Divergence Trading Strategy -> `fmz_442946_ao_one_bar_divergence_stoch_filter_reversal`

- FMZ source id: 442946 (lineage).
- Source: https://www.fmz.com/strategy/442946 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 15:51:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | AO divergence with a stochastic filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [14, 9] x `oversold` [20, 30]: **4 trials** (overbought = 100 - oversold); the AO lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
