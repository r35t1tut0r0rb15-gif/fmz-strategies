# #437039 Multi Timeframe Momentum Breakout Strategy -> `fmz_437039_rsi63_40_dmi_adx_short_atr_bracket_reversal`

- FMZ source id: 437039 (lineage).
- Source: https://www.fmz.com/strategy/437039 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 16:56:09). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only ATR bracket at the signal bar |
| 2 | PASS | RSI momentum with DMI / ADX confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_long` [63.0, 60.0] x `di_threshold` [25.0, 20.0]: **4 trials**; RSI short 40, ADX 20, SL 1.5 ATR, TP 4 ATR.

## Ambiguities resolved

- Shared exit id: short-only bracket. Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_threshold"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
