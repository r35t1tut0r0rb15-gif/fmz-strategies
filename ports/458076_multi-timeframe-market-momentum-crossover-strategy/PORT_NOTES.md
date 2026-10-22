# #458076 Multi Timeframe Market Momentum Crossover Strategy -> `fmz_458076_macd_signal_cross_beyond_zero_session_tick_bracket_reversal`

- FMZ source id: 458076 (lineage).
- Source: https://www.fmz.com/strategy/458076 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:10:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | MACD signal crossings beyond zero in set hours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed 1-contract quantity and the unused risk amount stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.0067, 1.0] x `tp_atr` [0.01, 1.5]: **4 trials**; the MACD lengths and the hours fixed.

## Ambiguities resolved

- Ticks as ATR multiples (1h ~150); session on the UTC bar open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
