# #458255 Multi Indicator Comprehensive Momentum Trading Strategy -> `fmz_458255_ema_macd_rsi_agreement_atr_bracket_reversal`

- FMZ source id: 458255 (lineage).
- Source: https://www.fmz.com/strategy/458255 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 12:01:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at entry |
| 2 | PASS | EMA, MACD and RSI agreement with an ATR bracket |
| 3 | PASS | Exchange pair in the header only (Bank Nifty named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `rsi_len` [14, 7]: **4 trials**; the EMA and MACD lengths fixed.

## Ambiguities resolved

- Opening bracket kept while signals repeat (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
