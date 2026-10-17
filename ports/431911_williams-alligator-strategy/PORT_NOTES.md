# #431911 Williams Alligator Strategy -> `fmz_431911_three_sma_alignment`

- FMZ source id: 431911 (lineage).
- Source: https://www.fmz.com/strategy/431911 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-13 10:58:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA alignment |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [50, 20] x `len3` [200, 100]: **4 trials**; SMA 100 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
