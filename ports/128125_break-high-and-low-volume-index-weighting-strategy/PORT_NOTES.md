# #128125 Break High and Low Volume Index Weighting Strategy -> `fmz_128125_volume_momentum_ema_sign_range_break_pct_stop_reversal`

- FMZ source id: 128125 (lineage).
- Source: https://www.fmz.com/strategy/128125 (MyLanguage, author 阿基米德的浴缸, FMZ last
  modified 2018-12-15 15:42:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stops against the signal close |
| 2 | PASS | Volume-weighted momentum sign with range breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | LOTS = max(MINAMOUNT, MONEYTOT / O x 0.8) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [100, 300] x `sloss` [2.0, 4.0]: **4 trials**; NC 50.

## Ambiguities resolved

- N = 100 from the backtest args (input default 300 in the grid). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
