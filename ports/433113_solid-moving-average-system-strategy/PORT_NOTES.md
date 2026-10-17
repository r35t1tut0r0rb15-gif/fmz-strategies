# #433113 Solid Moving Average System Strategy -> `fmz_433113_smma_stack_london_close`

- FMZ source id: 433113 (lineage).
- Source: https://www.fmz.com/strategy/433113 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 15:11:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; explicit time exits |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["UTC", "America/New_York"] x `atr_k` [0.15, 1.0]: **4 trials**; the averages and the window fixed.

## Ambiguities resolved

- Entries at any time, close-out outside 03:00-10:45 (UTC or New York, both declared); tick bracket as ATR. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
