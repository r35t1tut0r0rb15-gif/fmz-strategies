# #437680 Trend and Oscillation Double Strategy -> `fmz_437680_trend_surfers_trail_state_trend_osc_1m_reversal`

- FMZ source id: 437680 (lineage).
- Source: https://www.fmz.com/strategy/437680 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-04 17:32:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 100 % target from the fill |
| 2 | PASS | Breakout-trail state with a DI trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity / close x leverage 1, commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hl_period` [168, 100] x `trail_mult` [8.0, 4.0]: **4 trials**; trailing ATR 10, fixed ATR 10 x 2, DI 14, TP 100 %.

## Ambiguities resolved

- Internal Trend Surfers state as written. Volume not used. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout_trail"`.

## Marks

`none`
