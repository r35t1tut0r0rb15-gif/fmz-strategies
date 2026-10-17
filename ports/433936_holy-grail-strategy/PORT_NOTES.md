# #433936 Holy Grail Strategy -> `fmz_433936_holy_grail_adx_ema`

- FMZ source id: 433936 (lineage).
- Source: https://www.fmz.com/strategy/433936 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 15:27:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX level and EMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `target` [30, 20]: **4 trials**; DI / ADX 14 fixed.

## Ambiguities resolved

- Unused test period, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
