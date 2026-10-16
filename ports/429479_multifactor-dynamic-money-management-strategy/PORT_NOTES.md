# #429479 Multifactor Dynamic Money Management Strategy -> `fmz_429479_sar_ema_macd_rsi_bracket`

- FMZ source id: 429479 (lineage).
- Source: https://www.fmz.com/strategy/429479 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 15:09:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | The FX tick bracket -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-% sizing and the equity protector stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [5.0, 2.0] x `tp_atr` [5.0, 2.0]: **4 trials**; the indicator settings fixed.

## Ambiguities resolved

- Flat tracked through the bracket; opposite confluence closes. Money management not ported. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
