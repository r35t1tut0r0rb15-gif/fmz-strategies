# #436476 基于Donchian通道的海龟交易策略Turtle-Trading-Strategy-Based-on-Donchian-Channels -> `fmz_436476_donchian_ema_filter_atr_stop`

- FMZ source id: 436476 (lineage).
- Source: https://www.fmz.com/strategy/436476 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 10:57:52). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | REVIEW | Stop distance re-evaluated each bar in the script: fixed at the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`donchian_slow` [20, 40] x `atr_mult` [2.0, 3.0]: **4 trials**; fast channel 10, EMA 50 / 125 and ATR 20 fixed.

## Ambiguities resolved

- ATR stop fixed at the fill; pyramiding not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
