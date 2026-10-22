# #441958 Overlay Trend Signals Strategy -> `fmz_441958_dmi_cross_adx_ema_flag_state`

- FMZ source id: 441958 (lineage).
- Source: https://www.fmz.com/strategy/441958 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 10:00:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | DMI crossings with ADX / EMA filters and state flags |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [14, 21] x `ema_len` [26, 50]: **4 trials**; ADX levels fixed.

## Ambiguities resolved

- Flags in call order as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
