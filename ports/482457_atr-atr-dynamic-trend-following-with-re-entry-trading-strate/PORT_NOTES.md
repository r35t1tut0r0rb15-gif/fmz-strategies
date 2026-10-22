# #482457 ATR动态趋势跟踪与重入场交易策略-ATR-Dynamic-Trend-Following-with-Re-entry-Trading-Strategy -> `fmz_482457_sma10_high_atr_band_breakout_close_rearm_bracket_long`

- FMZ source id: 482457 (lineage).
- Source: https://www.fmz.com/strategy/482457 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:11:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | ATR-banded SMA breakouts with a close-gated re-arm |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `target_multiplier` [0, 2]: **4 trials**; band sma(atr 200, 200) x 0.8, stop 2 bands.

## Ambiguities resolved

- The re-entry branch can never fire (entryPrice is na when it is tested), as written.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`coarse_bar_stop`
