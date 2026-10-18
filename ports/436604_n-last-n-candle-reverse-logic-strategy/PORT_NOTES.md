# #436604 最后N只烛的逆向逻辑策略Last-N-Candle-Reverse-Logic-Strategy -> `fmz_436604_last_n_candles_run`

- FMZ source id: 436604 (lineage).
- Source: https://www.fmz.com/strategy/436604 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 11:00:29). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colour run |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The investment value and the quantity formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`num_check` [5, 3] x `num_exit` [2, 3]: **4 trials**; the inverse-logic switch (off) fixed.

## Ambiguities resolved

- Var counters carried across bars as written. Inverse logic not searched. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
