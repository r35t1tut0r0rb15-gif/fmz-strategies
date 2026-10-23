# #473146 VWAP-MACD-RSI多因子量化交易策略-VWAP-MACD-RSI-Multi-Factor-Quantitative-Trading-Strategy -> `fmz_473146_session_vwap_cross_macd_rsi_tight_bracket_4h_reversal`

- FMZ source id: 473146 (lineage).
- Source: https://www.fmz.com/strategy/473146 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:11:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | Session-VWAP crossings with MACD and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.005, 0.01] x `sl` [0.0025, 0.005]: **4 trials**; MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- Session VWAP reset on the broker day. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`coarse_bar_stop`
