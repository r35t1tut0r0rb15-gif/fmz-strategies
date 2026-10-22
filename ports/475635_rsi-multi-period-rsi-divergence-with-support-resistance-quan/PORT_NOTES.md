# #475635 多周期RSI背离与支撑阻力组合量化策略-Multi-Period-RSI-Divergence-with-Support-Resistance-Quantitative-Trading-Strategy -> `fmz_475635_rsi14_window_divergence_sr50_pct_bracket_reversal`

- FMZ source id: 475635 (lineage).
- Source: https://www.fmz.com/strategy/475635 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 17:01:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Window RSI divergences with support / resistance filters and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `sr_length` [50, 100]: **4 trials**; stop 1 %, target 2 %.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
