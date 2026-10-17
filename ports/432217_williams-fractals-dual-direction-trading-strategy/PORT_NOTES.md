# #432217 Williams Fractals Dual Direction Trading Strategy -> `fmz_432217_williams_fractal_ema_trend`

- FMZ source id: 432217 (lineage).
- Source: https://www.fmz.com/strategy/432217 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 16:22:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Fractals, EMA order, RSI turn and percentage exits of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1000 USD cash per trade stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432217. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.5, 1.5] x `sl_pct` [3.1, 1.5]: **4 trials**; fractal periods 2, EMA 20 / 50 / 100 and RSI 14 fixed.

## Ambiguities resolved

- Entries from flat, the bracket followed on bars. The bracket is live on the fill bar in the house engine. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
