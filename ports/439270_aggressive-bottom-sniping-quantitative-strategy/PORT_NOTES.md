# #439270 Aggressive Bottom Sniping Quantitative Strategy -> `fmz_439270_volume_spike_oversold_rsi20_10bar_hold_1m_long_only`

- FMZ source id: 439270 (lineage).
- Source: https://www.fmz.com/strategy/439270 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 16:25:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; time exit after 10 bars |
| 2 | PASS | Volume spikes into an oversold RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `close_time` [10, 30]: **4 trials**; volume SMA 20, RSI 20 under 30.

## Ambiguities resolved

- Hold of 10 bars counted from the fill bar. Volume = broker tick volume. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback_time_exit"`.

## Marks

`none`
