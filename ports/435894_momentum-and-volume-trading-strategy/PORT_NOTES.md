# #435894 Momentum and Volume Trading Strategy -> `fmz_435894_momentum_zero_cross_volume_spike_short_bracket_reversal`

- FMZ source id: 435894 (lineage).
- Source: https://www.fmz.com/strategy/435894 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-19 15:37:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket at the signal close |
| 2 | PASS | Momentum zero crossings on volume spikes |
| 3 | PASS | Exchange pair in the header only; tick distances converted at the source's tick. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_threshold` [2.0, 1.5] x `vol_len` [20, 50]: **4 trials**; short bracket 0.08 % / 0.05 %.

## Ambiguities resolved

- Shared exit id (short-only bracket); tick distances without / mintick. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
