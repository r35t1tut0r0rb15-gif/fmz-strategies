# #477945 Multi Period Bollinger Bands Trend Breakout Strategy with Volatility Risk Control Model -> `fmz_477945_bb20_breakout_no_squeeze_atr_bracket_reversal`

- FMZ source id: 477945 (lineage).
- Source: https://www.fmz.com/strategy/477945 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:12:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | Bollinger breakouts outside a squeeze with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk 1 % qty stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rr` [2.0, 3.0]: **4 trials**; 2 sd, ATR 14, stop 1 ATR.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
