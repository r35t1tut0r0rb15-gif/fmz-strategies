# #439830 Momentum Moving Average Crossover Trading Strategy -> `fmz_439830_tradersposts_ema8_21_cross`

- FMZ source id: 439830 (lineage).
- Source: https://www.fmz.com/strategy/439830 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 11:09:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the lookahead lines unused |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop / target inputs stored (0). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439830. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Zero stop / target inputs place no exits. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
