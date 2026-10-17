# #431964 Gradual Stop Loss Movement Strategy -> `fmz_431964_sma_cross_stepped_stop`

- FMZ source id: 431964 (lineage).
- Source: https://www.fmz.com/strategy/431964 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-13 17:30:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stepped stop's first step fixed (rule 2) |
| 2 | PASS | SMA crosses and percentage steps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `first_step` [5.0, 2.5]: **4 trials**; SMA 28 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop stepped up by the 7-bar low; the first 5 % step kept. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
