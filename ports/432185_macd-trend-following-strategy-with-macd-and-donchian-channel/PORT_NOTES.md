# #432185 基于MACD的扩散通道趋势跟踪策略Trend-Following-Strategy-with-MACD-and-Donchian-Channel -> `fmz_432185_donchian_macd_atr_stop`

- FMZ source id: 432185 (lineage).
- Source: https://www.fmz.com/strategy/432185 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 11:37:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (the re-set pending) |
| 2 | PASS | ATR stop, channel and MACD side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based amount and pyramiding 3 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [50, 20] x `sl_atr` [4.0, 2.0]: **4 trials**; MACD 12 / 26 / 9 and ATR 14 fixed.

## Ambiguities resolved

- macd read as non-zero. Pending (not emitted as written): the stop re-set on each later signal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
