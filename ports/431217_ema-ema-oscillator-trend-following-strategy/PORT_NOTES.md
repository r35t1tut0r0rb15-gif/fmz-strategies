# #431217 基于EMA指标的趋势追踪策略EMA-Oscillator-Trend-Following-Strategy -> `fmz_431217_ema_oscillator_oversold_long`

- FMZ source id: 431217 (lineage).
- Source: https://www.fmz.com/strategy/431217 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 09:53:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | A deviation-scaled oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 30 % of equity and pyramiding 3 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `factor` [1.7, 2.5]: **4 trials**; the oversold model fixed.

## Ambiguities resolved

- Adds not ported; entry and close on one bar as stated. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`
