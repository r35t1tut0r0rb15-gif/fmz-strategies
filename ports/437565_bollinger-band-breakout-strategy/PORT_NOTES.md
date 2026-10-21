# #437565 Bollinger Band Breakout Strategy -> `fmz_437565_bb_breakout_band_exit_long`

- FMZ source id: 437565 (lineage).
- Source: https://www.fmz.com/strategy/437565 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 17:53:32). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG437565, ND426339. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.0] x `exit_option` [1, 2]: **4 trials**; period 20 fixed.

## Ambiguities resolved

- Exit option swept (1 lower band, 2 middle band). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
