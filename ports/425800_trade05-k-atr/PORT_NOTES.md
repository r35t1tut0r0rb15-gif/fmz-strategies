# #425800 Trade05-K线支撑阻力ATR止盈 -> `fmz_425800_weighted_price_support_resistance_break_atr50_target_reversal`

- FMZ source id: 425800 (lineage).
- Source: https://www.fmz.com/strategy/425800 (MyLanguage, author 作手君TradeMan, FMZ last
  modified 2023-09-04 22:33:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weighted-price support / resistance breakout with an ATR target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | LOTS = max(1, intpart(percent / 100 x MONEY x C / (MARGIN x UNIT))) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lenth` [250, 100] x `atrs` [50, 20]: **4 trials**.

## Ambiguities resolved

- BKVOL <= 1 read as not long; the target uses the current ATR, as written. Volume = broker tick volume (VOL > 0).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
