# #362022 EMA bands leledc bollinger bands trend catching strategy -> `fmz_362022_ema34_high_low_band_break_reversal`

- FMZ source id: 362022 (lineage).
- Source: https://www.fmz.com/strategy/362022 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 16:48:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA high / low band breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the commented strategy() line holds 100 % of equity). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG362022. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [34, 55] x `use_slow_ema` [0, 1]: **4 trials**; slow EMA 200 as the source's own switch.

## Ambiguities resolved

- Default options only; the Leledc volume filter is off (volume not used). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
