# #430833 Dual Pressure Quantitative Trading Strategy -> `fmz_430833_stoch_volume_ema_cross_state_machine_long`

- FMZ source id: 430833 (lineage).
- Source: https://www.fmz.com/strategy/430833 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-02 13:56:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop |
| 2 | PASS | Stochastic turns with volume confirmation and EMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission 0.25 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_factor` [80.0, 40.0] x `threshold_sl` [6.0, 3.0]: **4 trials**; stoch 14 / 3, EMA 14 / 23.

## Ambiguities resolved

- The script's bought state as written. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_trend"`.

## Marks

`none`
