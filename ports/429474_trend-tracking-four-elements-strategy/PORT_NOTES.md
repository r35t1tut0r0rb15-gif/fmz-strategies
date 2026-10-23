# #429474 Trend Tracking Four Elements Strategy -> `fmz_429474_sar_ma200_50_squeeze_hawkeye_volume_agreement_reversal`

- FMZ source id: 429474 (lineage).
- Source: https://www.fmz.com/strategy/429474 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 14:47:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target from the fill |
| 2 | PASS | SAR / MA / squeeze / volume-bar agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_hvi` [200, 100] x `ma_1_val` [200, 100]: **4 trials**; SMA 50, squeeze 20, SAR code 1.

## Ambiguities resolved

- high < SAR for longs, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
