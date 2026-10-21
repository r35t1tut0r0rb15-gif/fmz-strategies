# #437774 Golden Ratio Moving Average Trading Strategy -> `fmz_437774_rsi3_dip_above_sma200_long`

- FMZ source id: 437774 (lineage).
- Source: https://www.fmz.com/strategy/437774 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 14:21:52). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | SMA sides and RSI level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the unused profit input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop` [0.2, 0.1] x `mashort` [10, 5]: **4 trials**; SMA 200 and RSI 3 < 30 fixed.

## Ambiguities resolved

- Percent stop fixed at entry; unused profit input. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
