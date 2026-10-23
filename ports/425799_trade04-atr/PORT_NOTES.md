# #425799 Trade04-双均线ATR通道高低点 -> `fmz_425799_day_open_atr_channel_ema12_120_high_low_break_reversal`

- FMZ source id: 425799 (lineage).
- Source: https://www.fmz.com/strategy/425799 (MyLanguage, author 作手君TradeMan, FMZ last
  modified 2023-09-04 22:33:38). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Day-open ATR channel breakout with an EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | LOTS = max(1, intpart(percent / 100 x MONEY x C / (MARGIN x UNIT))) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [12, 20] x `x` [3.0, 2.0]: **4 trials**; LENGTH2 = 10 x LENGTH1.

## Ambiguities resolved

- The day is the broker day. Statements apply in order (no AUTOFILTER). Volume = broker tick volume (VOL > 0).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
