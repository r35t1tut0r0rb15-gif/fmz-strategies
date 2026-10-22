# #482459 Dynamic Trend Channel and Relative Strength Momentum Trading Strategy -> `fmz_482459_keltner20_reentry_rsi30_70_mid_exit_reversal`

- FMZ source id: 482459 (lineage).
- Source: https://www.fmz.com/strategy/482459 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:15:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner re-entries with RSI extremes and mid-line exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [1.5, 2.0] x `ema_length` [20, 50]: **4 trials**; ATR 10, RSI 14, 70 / 30 / 50.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_reversion"`.

## Marks

`none`
