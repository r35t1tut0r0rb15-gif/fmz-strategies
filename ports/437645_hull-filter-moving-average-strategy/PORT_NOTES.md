# #437645 Hull Filter Moving Average Strategy -> `fmz_437645_hull_turn_hull_trend_bracket`

- FMZ source id: 437645 (lineage).
- Source: https://www.fmz.com/strategy/437645 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:16:34). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick-scaled ATR bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the factor inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [20.0, 2.0] x `signal_period` [50, 30]: **4 trials**; filter 200, ATR 14 and the 3 / 2 target ratio fixed.

## Ambiguities resolved

- Tick-scaled bracket: reading 20 ATR (BTC tick) and intent 2 ATR; window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
