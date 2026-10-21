# #438944 Super Trend Dual Moving Average Strategy -> `fmz_438944_supertrend_state_sma200_stop`

- FMZ source id: 438944 (lineage).
- Source: https://www.fmz.com/strategy/438944 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-16 15:19:09). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | ATR trend state and SMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `sl` [0.25, 0.10]: **4 trials**; ATR 10 and SMA 200 fixed.

## Ambiguities resolved

- Level-state entries; the 25 % stop started at the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
