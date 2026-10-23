# #426920 Multi indicator Trend Following Strategy with Stop Loss and Take Profit -> `fmz_426920_sma_macd_hist_zero_turn_ema200_sar_volume_osc_sar_bracket_reversal`

- FMZ source id: 426920 (lineage).
- Source: https://www.fmz.com/strategy/426920 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 15:39:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based SAR target / stop |
| 2 | PASS | MACD histogram turns with EMA 200, SAR and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000, commission 0.00005 per contract stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lena` [200, 100] x `longlen` [8, 20]: **4 trials**; MACD 12 / 25 / 9 (SMA), SAR 0.1 / 0.05 / 0.3.

## Ambiguities resolved

- Counters start at na (the first trade waits for an opposite signal), as written. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
