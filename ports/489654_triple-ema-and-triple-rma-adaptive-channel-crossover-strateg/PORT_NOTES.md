# #489654 Triple EMA and Triple RMA Adaptive Channel Crossover Strategy -> `fmz_489654_ema3_rma3_atr_channel_breakout_open_stop_flat`

- FMZ source id: 489654 (lineage).
- Source: https://www.fmz.com/strategy/489654 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 13:43:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-open stop as a fraction of the fill |
| 2 | PASS | Short-channel breakouts with an open-based stop and exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_mult` [1.5, 2.5] x `atr_len` [3, 10]: **4 trials**; EMA / RMA 3, RMA multiplier 1.0.

## Ambiguities resolved

- Entries only from flat (a loop follows the stop and open-crossing exits). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`coarse_bar_stop`
