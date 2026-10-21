# #437494 Stiffness Breakthrough Strategy -> `fmz_437494_stiffness_threshold`

- FMZ source id: 437494 (lineage).
- Source: https://www.fmz.com/strategy/437494 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 11:34:34). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Share-of-bars index levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [100, 50] x `stiff_length` [60, 30]: **4 trials**; smoothing 3 and threshold 90 fixed.

## Ambiguities resolved

- Call-order fills. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
