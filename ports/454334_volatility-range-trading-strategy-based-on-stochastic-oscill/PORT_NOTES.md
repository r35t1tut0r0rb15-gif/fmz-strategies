# #454334 Volatility Range Trading Strategy Based on Stochastic Oscillator -> `fmz_454334_stoch_extreme_spaced_from_flat_atr_bracket`

- FMZ source id: 454334 (lineage).
- Source: https://www.fmz.com/strategy/454334 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 14:52:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR bracket as fractions of the signal close |
| 2 | PASS | Stochastic extremes with entry spacing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [14, 7] x `gap_bars` [20, 5] x `atr_mult` [2.0, 1.0]: **8 trials**; the levels fixed.

## Ambiguities resolved

- Entries only from flat, spaced. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
