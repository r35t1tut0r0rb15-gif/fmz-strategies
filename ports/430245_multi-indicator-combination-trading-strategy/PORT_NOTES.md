# #430245 Multi indicator Combination Trading Strategy -> `fmz_430245_adx_di_cci_ao_dip_long`

- FMZ source id: 430245 (lineage).
- Source: https://www.fmz.com/strategy/430245 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-26 15:22:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ADX / DI levels, a CCI and an oscillator sign. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Floor(equity / close) per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_above` [25, 20] x `di_below` [10, 15]: **4 trials**; DI+ exit 25, CCI 20, AO 5 / 34 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
