# #429773 黄金VWAP-MACD-SMO交易策略Gold-VWAP-MACD-SMO-Trading-Strategy -> `fmz_429773_monthly_vwap_macd_hist_smi_short_bracket_reversal`

- FMZ source id: 429773 (lineage).
- Source: https://www.fmz.com/strategy/429773 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 16:23:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket from the signal close |
| 2 | PASS | Monthly VWAP side with MACD and SMI momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (10000 % of equity) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tpshort` [0.05, 0.03] x `slshort` [0.025, 0.04]: **4 trials**; MACD 12 / 26 / 9, TSI 6 / 22 / 5.

## Ambiguities resolved

- The shared exit id leaves longs without a bracket, as written (weird case). Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_trend"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
