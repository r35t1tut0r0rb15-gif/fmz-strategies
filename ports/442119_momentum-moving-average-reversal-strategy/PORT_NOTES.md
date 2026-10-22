# #442119 Momentum Moving Average Reversal Strategy -> `fmz_442119_sma9_side_rsi40_pct_bracket_long`

- FMZ source id: 442119 (lineage).
- Source: https://www.fmz.com/strategy/442119 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 14:59:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | SMA side, RSI level and percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.015, 0.03] x `tp` [0.03, 0.06]: **4 trials**; SMA 9 and RSI 14 fixed.

## Ambiguities resolved

- Bracket active from the fill bar. Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
