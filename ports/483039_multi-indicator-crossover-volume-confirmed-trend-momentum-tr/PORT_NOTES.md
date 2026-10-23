# #483039 Multi Indicator Crossover Volume Confirmed Trend Momentum Trading Strategy -> `fmz_483039_macd_cross_rsi_stochrsi_volume_spike_reversal`

- FMZ source id: 483039 (lineage).
- Source: https://www.fmz.com/strategy/483039 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 10:34:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings confirmed by RSI, stochastic RSI and a volume spike |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [1.5, 1.0] x `stoch_len` [14, 21]: **4 trials**; MACD 12 / 26 / 9, RSI 14, K / D 3.

## Ambiguities resolved

- Entries only. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
