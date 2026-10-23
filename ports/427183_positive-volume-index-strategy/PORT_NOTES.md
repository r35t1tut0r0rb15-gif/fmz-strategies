# #427183 Positive Volume Index Strategy -> `fmz_427183_positive_volume_index_ema255_state_reversal`

- FMZ source id: 427183 (lineage).
- Source: https://www.fmz.com/strategy/427183 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 21:21:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Positive volume index against its EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427183. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [255, 100]: **2 trials**.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_index"`.

## Marks

`none`
