# #483061 Trend Breakout Trading Strategy Based on Donchian Channel and Moving Average -> `fmz_483061_donchian20_expansion_sma200_side_reversal`

- FMZ source id: 483061 (lineage).
- Source: https://www.fmz.com/strategy/483061 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:07:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the channel stops pending |
| 2 | PASS | Donchian channel expansions with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `sma_length` [200, 100]: **4 trials**.

## Ambiguities resolved

- The per-bar channel stops are pending, not ported. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
