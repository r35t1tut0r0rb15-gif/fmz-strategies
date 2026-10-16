# #430170 动量追踪CCI策略Momentum-Tracking-CCI-Strategy -> `fmz_430170_cci_turn_ema_pct_bracket`

- FMZ source id: 430170 (lineage).
- Source: https://www.fmz.com/strategy/430170 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 17:37:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed percentage bracket. |
| 2 | PASS | CCI levels, an EMA and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 10 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `tp_sl_pct` [10.0, 5.0]: **4 trials**; levels 150 / -140 and EMA 55 fixed; TP = SL.

## Ambiguities resolved

- Same-side entry and close on one bar: the entry is kept (approximation). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
