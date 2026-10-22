# #477612 Multi Technical Indicator Momentum MA Trend Following Strategy -> `fmz_477612_macd_crossup_rsi50_sma50_200_pct_bracket_long`

- FMZ source id: 477612 (lineage).
- Source: https://www.fmz.com/strategy/477612 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 16:56:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | MACD cross-ups with RSI and SMA trend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / risk inputs unused; the bracket fractions stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.02, 0.03] x `sl_pct` [0.01, 0.005]: **4 trials**; MACD 12 / 26 / 9, RSI 14, SMA 50 / 200.

## Ambiguities resolved

- Only TP1 and its stop act. Repeat-signal re-sends not followed. Long only. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
