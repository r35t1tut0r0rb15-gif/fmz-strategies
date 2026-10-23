# #428621 力道K线突破策略Choppiness-K-line-Breakthrough-Strategy -> `fmz_428621_session_counter_candle_mfi14_choppiness_volume_squareoff_reversal`

- FMZ source id: 428621 (lineage).
- Source: https://www.fmz.com/strategy/428621 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 15:59:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; session square-off |
| 2 | PASS | Counter-candle money-flow extremes in a non-choppy market |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [25, 20] x `trend_factor` [50, 40]: **4 trials**; overbought 100 - oversold, length 14.

## Ambiguities resolved

- Session in UTC by bar open; the repeat-signal bracket is not ported (weird case). Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "session_reversal"`.

## Marks

`none`
