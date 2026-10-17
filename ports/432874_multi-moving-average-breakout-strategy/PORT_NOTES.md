# #432874 Multi Moving Average Breakout Strategy -> `fmz_432874_four_sma_close_cross`

- FMZ source id: 432874 (lineage).
- Source: https://www.fmz.com/strategy/432874 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-22 13:41:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the unreachable exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432874. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`set` [0, 1]: **2 trials**; 0 = SMA 21 / 50 / 100 / 200 as written, 1 = 10 / 20 / 50 / 100.

## Ambiguities resolved

- The exit conditions can never be true. The later short wins a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
