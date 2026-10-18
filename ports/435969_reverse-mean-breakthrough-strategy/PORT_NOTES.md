# #435969 Reverse Mean Breakthrough Strategy -> `fmz_435969_cci_cross_mean_channel_fade`

- FMZ source id: 435969 (lineage).
- Source: https://www.fmz.com/strategy/435969 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 14:48:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Price-unit stop -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The pip stop input quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430176. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.05, 1.0] x `band_mult` [1.6, 2.0]: **4 trials**; CCI 10, RSI 14 at 35 / 65 and EMA 200 fixed.

## Ambiguities resolved

- Both-direction cross; price-unit stop -> ATR multiple; band touch as an exit signal. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
