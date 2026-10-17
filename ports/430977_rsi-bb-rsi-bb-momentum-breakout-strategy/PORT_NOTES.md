# #430977 RSI-BB动量突破策略RSI-BB-Momentum-Breakout-Strategy -> `fmz_430977_rsi_bb_impulse`

- FMZ source id: 430977 (lineage).
- Source: https://www.fmz.com/strategy/430977 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-03 15:02:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick target / stop -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.07, 1.0] x `tp_atr` [0.8, 2.0]: **4 trials**; BB 50 / 0.2, RSI 30 and the impulse bands fixed.

## Ambiguities resolved

- Tick bracket as ATR fractions of the signal bar (criterion 2 ADAPT). Mark coarse_bar_stop. REVERSAL INTENDED.
  FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
