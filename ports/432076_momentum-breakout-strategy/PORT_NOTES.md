# #432076 Momentum Breakout Strategy -> `fmz_432076_ut_bot_atr_line`

- FMZ source id: 432076 (lineage).
- Source: https://www.fmz.com/strategy/432076 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 11:19:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_len` [10, 20]: **4 trials**.

## Ambiguities resolved

- Inert %B filter as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
