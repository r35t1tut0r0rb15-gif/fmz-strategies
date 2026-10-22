# #442507 Log Ichimoku Cross Variety Strategy -> `fmz_442507_log_ichimoku_span_cross_reversal`

- FMZ source id: 442507 (lineage).
- Source: https://www.fmz.com/strategy/442507 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-22 13:53:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Log-price span crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `span_b` [52, 120]: **4 trials**; the base line 26 fixed.

## Ambiguities resolved

- Undisplaced spans as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
