# #489654 三重指数移动平均与三重相对移动平均自适应通道交叉策略-Triple-EMA-and-Triple-RMA-Adaptive-Channel-Crossover-Strategy -> `fmz_489654_ema3_rma3_atr_channel_open_stop`

- FMZ source id: 489654 (lineage).
- Source: https://www.fmz.com/strategy/489654 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-07 13:43:30). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal bar. |
| 2 | PASS | ATR channels and bar levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 0.5 %-risk quantity quoted; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_mult` [1.5, 2.5] x `rma_mult` [1.0, 2.0]: **4 trials**; defaults 1.5 / 1.0 (the source's); EMA 3, RMA 3 and
ATR 3 fixed.

## Ambiguities resolved

- The stop is the signal bar's open (re-based on the fill); a signal bar closing on the wrong side of its open (or
  at it: na quantity) emits no entry.
- Entries only from flat: simulate() follows the house stop on bars; the prev-open crosses are close-checked exits,
  from the fill bar. A buy wins over a sell on one bar. Opposite entries cannot occur.
- Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_band_breakout"`.

## Marks

`coarse_bar_stop`
