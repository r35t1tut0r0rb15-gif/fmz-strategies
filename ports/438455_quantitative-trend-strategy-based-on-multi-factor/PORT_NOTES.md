# #438455 Quantitative Trend Strategy Based on Multi factor -> `fmz_438455_vsa_reverse_upthrust_low_volume_test_1h_long_only`

- FMZ source id: 438455 (lineage).
- Source: https://www.fmz.com/strategy/438455 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-12 11:09:40). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-spread-analysis bar patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_len` [40, 20] x `spread_len` [80, 40]: **4 trials**; random-walk index 2 / 8 and 10 / 40.

## Ambiguities resolved

- Only the order-feeding VSA labels are ported; upmajor / upminor as written (na -> 0 / -1). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
