# #430585 Tesla Supertrend Strategy -> `fmz_430585_supertrend_rsi_adx_long`

- FMZ source id: 430585 (lineage).
- Source: https://www.fmz.com/strategy/430585 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 15:46:31). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR bands, RSI and ADX levels. |
| 3 | PASS | "Tesla" in the title only; exchange pair in the header. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430585. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [19, 10] x `factor` [3.0, 2.0]: **4 trials**; the RSI and ADX filters fixed.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
