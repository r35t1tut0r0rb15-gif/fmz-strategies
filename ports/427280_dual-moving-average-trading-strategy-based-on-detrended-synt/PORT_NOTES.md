# #427280 Dual Moving Average Trading Strategy Based on Detrended Synthetic Price -> `fmz_427280_detrended_synthetic_price`

- FMZ source id: 427280 (lineage).
- Source: https://www.fmz.com/strategy/427280 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 17:13:28). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | +-25 price-unit bands -> +- `band_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `band_atr` [2, 1, 4]: **6 trials**; defaults 14 / 2.

## Ambiguities resolved

- Bands in price units re-expressed in ATR (25 USD on 1-minute BTC bars is about 1-3 ATR; judgement before any backtest).
- As written, above the "SellBand" buys. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks

`none`
