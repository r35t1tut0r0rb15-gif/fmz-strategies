# #437661 基于布林带和VWAP的量化交易策略Bollinger-Bands-and-VWAP-based-Quantitative-Trading-Strategy -> `fmz_437661_ema_uptrend_vwap_bb_dip_upper_band_exit_long`

- FMZ source id: 437661 (lineage).
- Source: https://www.fmz.com/strategy/437661 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:59:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA uptrend dip-and-recovery entries with a band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): fixed qty 3, pyramiding 2 (adds), capital 10000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 50] x `dip_bars` [10, 5]: **4 trials**; EMA 50 / 200, BB 2 sd.

## Ambiguities resolved

- Dip test against the current band; the misnamed stop never acts. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
