# #436609 Bollinger Bands Momentum Trend Following Strategy -> `fmz_436609_bb20_breakout_wma99_atr_stop_reversal`

- FMZ source id: 436609 (lineage).
- Source: https://www.fmz.com/strategy/436609 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-26 11:21:10). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the fill |
| 2 | PASS | Bollinger breakouts with a WMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 2 % / (2 x ATR 14), commission 0.2 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 50] x `ma_len` [99, 200]: **4 trials**; BB 2 sd, ATR 14 x 2.

## Ambiguities resolved

- ATR at the signal bar. Volume not used (filter off). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
