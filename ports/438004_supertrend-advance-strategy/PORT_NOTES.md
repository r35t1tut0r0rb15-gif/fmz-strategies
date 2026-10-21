# #438004 Supertrend Advance Strategy -> `fmz_438004_supertrend_pullback_filters_bracket`

- FMZ source id: 438004 (lineage).
- Source: https://www.fmz.com/strategy/438004 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 10:03:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | SuperTrend, EMA, RSI, MACD and CCI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, the quantity input and the unselected exit types stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `cci_level` [200, 100]: **4 trials**; ATR 10, EMA 200, RSI 14 at 50, MACD 12 / 26 / 9, CCI 20 and the 1 % / 2 % bracket fixed.

## Ambiguities resolved

- Percentage bracket fixed at the fill (the original arms it one bar later); other exit types not selected. Entries only from flat. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
