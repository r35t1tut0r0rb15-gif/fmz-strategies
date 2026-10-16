# #427810 BB Keltner Squeeze Trading Strategy -> `fmz_427810_bb_keltner_squeeze_release`

- FMZ source id: 427810 (lineage).
- Source: https://www.fmz.com/strategy/427810 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-25 17:38:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Standard deviations and true-range multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Initial capital only stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `bb_mult` [2, 1.5] x `k_mult` [1.5, 2]: **8 trials**; defaults 20 / 2 / 1.5 (the source's).

## Ambiguities resolved

- `direction` is midc[1] each bar (not var). Opposite entries cannot occur (entries follow a squeeze bar).
- Oscillator and year inputs unused. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
