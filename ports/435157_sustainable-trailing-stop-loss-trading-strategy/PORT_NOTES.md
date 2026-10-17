# #435157 Sustainable Trailing Stop Loss Trading Strategy -> `fmz_435157_always_in_ratchet_template`

- FMZ source id: 435157 (lineage).
- Source: https://www.fmz.com/strategy/435157 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 17:29:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet on closes |
| 2 | PASS | Percent stops |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`side` ["LONG", "SHORT"] x `init_sl` [3.0, 6.0]: **4 trials**.

## Ambiguities resolved

- Placeholder entries as written (always in after each exit); close-based ratchet. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "always_in_trailing_stop"`.

## Marks

`none`
