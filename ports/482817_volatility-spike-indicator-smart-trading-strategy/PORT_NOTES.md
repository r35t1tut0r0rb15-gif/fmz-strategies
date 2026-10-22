# #482817 Volatility Spike Indicator Smart Trading Strategy -> `fmz_482817_last_hour_wick_spike0_62_pct_bracket_reversal`

- FMZ source id: 482817 (lineage).
- Source: https://www.fmz.com/strategy/482817 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:43:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Hourly wick spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 30000 USDT per trade and 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`spike_threshold` [0.62, 1.0] x `profit_target` [0.42, 0.8]: **4 trials**; stop 1 %.

## Ambiguities resolved

- The lower-time-frame security without lookahead is the 3-hour bar's last hour.
- Brackets fixed from the fill, active from the fill bar. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop`
