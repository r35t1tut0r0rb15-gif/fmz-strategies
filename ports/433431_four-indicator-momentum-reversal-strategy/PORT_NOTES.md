# #433431 Four Indicator Momentum Reversal Strategy -> `fmz_433431_ema_4_8_rsi_cci_bracket`

- FMZ source id: 433431 (lineage).
- Source: https://www.fmz.com/strategy/433431 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 15:51:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.1, 1.0] x `sl_atr` [0.08, 0.8]: **4 trials**; EMA 4 / 8, RSI 14, CCI 14 and ATR 14 fixed.

## Ambiguities resolved

- Tick bracket as ATR fractions (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
