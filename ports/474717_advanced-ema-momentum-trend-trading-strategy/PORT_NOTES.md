# #474717 Advanced EMA Momentum Trend Trading Strategy -> `fmz_474717_momentum10_cross_ema200_pct_bracket_from_flat`

- FMZ source id: 474717 (lineage).
- Source: https://www.fmz.com/strategy/474717 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-11 17:50:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Momentum threshold crossings with an EMA filter and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed contract size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [10, 20] x `stop_pct` [1.0, 2.0]: **4 trials**; filters as fractions of 42000, TP ratio 2.

## Ambiguities resolved

- Momentum filters as fractions of 42000. Entries only from flat. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
