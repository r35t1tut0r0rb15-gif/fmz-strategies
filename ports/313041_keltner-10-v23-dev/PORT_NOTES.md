# #313041 Keltner通道突破止损加盈利10即长期持有策略-v23-dev-多周期 -> `fmz_313041_keltner80_x3_break_volume_surge_pct_stops_halt_long`

- FMZ source id: 313041 (lineage).
- Source: https://www.fmz.com/strategy/313041 (python, author nanpian, FMZ last
  modified 2021-09-02 12:04:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits; a terminal halt kept as written |
| 2 | PASS | Keltner breakouts with a volume surge filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 600 USDT per buy and balance tests stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k` [3.0, 2.0] x `vol_mult` [1.5, 2.0]: **4 trials**; EMA 80, stop 6 %, gain 10 %, +10 points.

## Ambiguities resolved

- The "return" halt keeps the long for good, as written (weird case). +10 points as a fraction of 42000.
- Forming-bar polling read on completed bars. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`none`
