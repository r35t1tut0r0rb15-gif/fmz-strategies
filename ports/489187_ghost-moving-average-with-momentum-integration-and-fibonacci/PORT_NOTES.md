# #489187 幽灵移动平均与动量结合的斐波那契目标价与止损策略-Ghost-Moving-Average-with-Momentum-Integration-and-Fibonacci-Target-Stop-Loss-Strategy -> `fmz_489187_ghost_ma_momentum_fib_bracket`

- FMZ source id: 489187 (lineage).
- Source: https://www.fmz.com/strategy/489187 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 15:33:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Moving averages, normalised momentum and range fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gma_len` [20, 40] x `swing` [50, 100]: **4 trials**; defaults 20 / 50 (the source's); momentum 20 / 10 and the
0.618 / 0.382 fractions fixed.

## Ambiguities resolved

- The bracket from the signal bar's 50-bar range (re-based on the fill); TP2 / TP3 are display only.
- Three-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509: `coarse_bar_stop`.
- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop`
