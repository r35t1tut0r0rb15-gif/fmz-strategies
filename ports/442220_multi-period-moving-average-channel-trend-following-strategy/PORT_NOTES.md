# #442220 Multi Period Moving Average Channel Trend Following Strategy -> `fmz_442220_seven_ma_high_low_channel_breakout_pct_bracket_1h_reversal`

- FMZ source id: 442220 (lineage).
- Source: https://www.fmz.com/strategy/442220 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 13:45:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | Breakouts of a seven-average high / low channel |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [12, 24] x `tp_long` [0.06, 0.03]: **4 trials**; SL long 5 %, TP / SL short 4.5 % / 5 %.

## Ambiguities resolved

- Bracket fixed at the signal close and followed in the signals. Volume = broker tick volume (VWMA). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_channel"`.

## Marks

`trailing_stop_pending`
