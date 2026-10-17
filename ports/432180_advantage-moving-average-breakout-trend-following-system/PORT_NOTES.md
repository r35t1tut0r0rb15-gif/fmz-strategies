# #432180 Advantage Moving Average Breakout Trend Following System -> `fmz_432180_donchian_ema_trend_atr_stop`

- FMZ source id: 432180 (lineage).
- Source: https://www.fmz.com/strategy/432180 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 11:00:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (the re-set pending) |
| 2 | PASS | ATR stop, channel and EMA rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based amount (1 % of 50,000 over 2 ATR) and pyramiding 4 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [50, 20] x `sl_atr` [4.0, 2.0]: **4 trials**; EMA 40 / 120 and ATR 14 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-set on each later signal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
