# #437386 Bollinger Bands Volume Confirmation Quantitative Trading Strategy -> `fmz_437386_bb20_breakout_volume_spike_daily_long`

- FMZ source id: 437386 (lineage).
- Source: https://www.fmz.com/strategy/437386 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-02 11:04:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts on volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `vol_mult` [2.0, 1.5]: **4 trials**; BB 2 sd.

## Ambiguities resolved

- Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
