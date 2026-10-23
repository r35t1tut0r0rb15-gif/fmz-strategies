# #442019 基于MACD和RSI的双确认入场策略Dual-Confirmation-MACD-and-RSI-Strategy -> `fmz_442019_candle_flip_macd5_13_cross_rsi_volume_1h_reversal`

- FMZ source id: 442019 (lineage).
- Source: https://www.fmz.com/strategy/442019 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 16:24:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-colour flips confirmed by MACD crossings, RSI and volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 12] x `slow` [13, 26]: **4 trials**; signal 5, RSI 14, volume SMA 20.

## Ambiguities resolved

- Closes on the next same-kind candle flip. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`none`
