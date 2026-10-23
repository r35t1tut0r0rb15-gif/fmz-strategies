# #437754 Breakout and Intelligent Bollinger Bands Price Channel Strategy -> `fmz_437754_displaced_bb14_reentry_volume_long`

- FMZ source id: 437754 (lineage).
- Source: https://www.fmz.com/strategy/437754 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 13:14:11). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Displaced Bollinger re-entries with a volume filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `displacement` [3, 1]: **4 trials**; deviations 2, multiplier 1, volume threshold 1.

## Ambiguities resolved

- Shorts close at once (stop below a short's entry); the sell signal closes the long. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
