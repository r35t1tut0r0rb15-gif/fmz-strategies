# #488520 Multi Indicator Volatility Breakout Trading System Based on Volume Price Relationship -> `fmz_488520_volspike_sum7_rsi_wick_atr_band_bracket_1h_reversal`

- FMZ source id: 488520 (lineage).
- Source: https://www.fmz.com/strategy/488520 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 15:33:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Extreme volume spikes with RSI and wick filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_back` [7, 5] x `atr_mult` [2.5, 1.5]: **4 trials**; RSI 14 20 / 80, wick ratio 2.

## Ambiguities resolved

- Stop and target both 2.5 ATR. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_spike"`.

## Marks

`none`
