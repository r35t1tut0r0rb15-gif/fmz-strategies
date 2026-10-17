# #431896 Twin Range Filter Trading Strategy -> `fmz_431896_twin_range_filter`

- FMZ source id: 431896 (lineage).
- Source: https://www.fmz.com/strategy/431896 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 10:38:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; close-checked time exit |
| 2 | ADAPT | Tick target / stop -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The floor(capital / close) order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.75, 3.0] x `max_bars` [17, 40]: **4 trials**; the stop = tp_atr / 3 (the source's 900 / 300); the range pairs and ATR filter fixed.

## Ambiguities resolved

- Tick bracket as ATR fractions (criterion 2 ADAPT); close-checked time exit. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "range_filter_trend"`.

## Marks

`none`
