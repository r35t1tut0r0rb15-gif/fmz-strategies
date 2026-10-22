# #474022 Multi EMA Trend Momentum Trading Strategy with Risk Management System -> `fmz_474022_ema_ribbon_rsi_stoch_atr_bracket_from_flat`

- FMZ source id: 474022 (lineage).
- Source: https://www.fmz.com/strategy/474022 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 14:52:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA ribbon trends with oscillator filters, bracket and close exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size from equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and multiples are constants).

## Ambiguities resolved

- No trail (offset only). Entries only from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
