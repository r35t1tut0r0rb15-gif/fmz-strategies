# #434998 Look Up and Look Down Strategy Based on Internal Price Channels -> `fmz_434998_inside_bar_sma_atr_bracket`

- FMZ source id: 434998 (lineage).
- Source: https://www.fmz.com/strategy/434998 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 15:56:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (approximation stated) |
| 2 | PASS | Inside bars, an average filter and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434998. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [65, 200] x `atr_mult` [5.0, 2.0]: **4 trials**; ATR 14 and TP 2 R fixed.

## Ambiguities resolved

- ATR stop from the signal bar (the script's is from the fill bar). REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
