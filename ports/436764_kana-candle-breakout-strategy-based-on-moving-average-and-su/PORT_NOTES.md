# #436764 Kana Candle Breakout Strategy Based on Moving Average and Support Resistance -> `fmz_436764_kana_bands_ha_range_position`

- FMZ source id: 436764 (lineage).
- Source: https://www.fmz.com/strategy/436764 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-27 15:27:45). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 4-hour values are 240 bars old |
| 2 | PASS | ATR bands and a range position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The take-profit tick formula (off) stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `use_sr` [True, False]: **4 trials**; multipliers 1 / 2 / 3, ATR 200, EMA 200, MACD 120 / 260 / 90 and the 240 S/R setting fixed.

## Ambiguities resolved

- Version-2 security reads the whole 4-hour bar, used 240 bars back; rsPos > 100 as written; call-order fills; take profit off. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
