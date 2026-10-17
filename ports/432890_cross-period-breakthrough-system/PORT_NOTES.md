# #432890 Cross Period Breakthrough System -> `fmz_432890_koala_smma_stack_window`

- FMZ source id: 432890 (lineage).
- Source: https://www.fmz.com/strategy/432890 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 15:22:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; explicit time exits |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot and the commission / slippage settings stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["UTC", "America/New_York"] x `atr_k` [0.15, 1.0]: **4 trials**; the averages and the windows fixed.

## Ambiguities resolved

- Session clock in UTC (header) or New York (the "london" reading), both declared. Tick bracket as ATR. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
