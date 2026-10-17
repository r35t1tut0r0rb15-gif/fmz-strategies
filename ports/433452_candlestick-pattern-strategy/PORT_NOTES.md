# #433452 Candlestick Pattern Strategy -> `fmz_433452_candle_patterns_bracket`

- FMZ source id: 433452 (lineage).
- Source: https://www.fmz.com/strategy/433452 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 18:26:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG433452. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.2, 1.0] x `tp_atr` [2.0, 1.0]: **4 trials**; all patterns on, ATR 14 fixed.

## Ambiguities resolved

- Tick bracket as ATR fractions (criterion 2 ADAPT); trail without offset dropped. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
