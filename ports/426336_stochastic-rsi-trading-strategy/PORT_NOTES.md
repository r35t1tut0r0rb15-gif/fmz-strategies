# #426336 Stochastic RSI Trading Strategy -> `fmz_426336_raw_stoch_rsi14_sma9_21_spread_session_vwap_side_reversal`

- FMZ source id: 426336 (lineage).
- Source: https://www.fmz.com/strategy/426336 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 11:57:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic-RSI turns with an SMA spread and VWAP side filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `os_level` [30.0, 20.0]: **4 trials**; overbought 100 - os_level (70 as written).

## Ambiguities resolved

- k unsmoothed, as written. VWAP anchored at the broker-day start. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
