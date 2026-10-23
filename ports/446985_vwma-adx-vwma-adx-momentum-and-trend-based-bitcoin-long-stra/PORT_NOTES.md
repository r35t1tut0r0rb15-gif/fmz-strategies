# #446985 VWMA-ADX-基于动量与趋势的比特币多头策略-VWMA-ADX-Momentum-and-Trend-Based-Bitcoin-Long-Strategy -> `fmz_446985_vwma9_14_cross_vwma_channel_dmi_volume_band_1h_long_only`

- FMZ source id: 446985 (lineage).
- Source: https://www.fmz.com/strategy/446985 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-03 17:47:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop at the signal bar as a fraction of the fill |
| 2 | PASS | VWMA crossings over a volume-weighted channel with volume and DMI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [66, 33] x `stop_k` [0.98, 0.95]: **4 trials**; VWMA 9 / 14 / 89, DMI 7 / 10.

## Ambiguities resolved

- 60-minute branches; DMI shifts as written; immediate close filled at the next open. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
