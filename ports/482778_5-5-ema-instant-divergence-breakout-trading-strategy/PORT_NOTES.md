# #482778 5均线即时背离突破交易策略-5-EMA-Instant-Divergence-Breakout-Trading-Strategy -> `fmz_482778_bar_beyond_ema5_range_3x_bracket_reversal`

- FMZ source id: 482778 (lineage).
- Source: https://www.fmz.com/strategy/482778 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:50:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar range bracket as fractions of the fill |
| 2 | PASS | Bars beyond the EMA 5 with a range bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin 100 / 100 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [5, 10] x `target_multiplier` [3.0, 1.5]: **4 trials**.

## Ambiguities resolved

- The trigger fires on its own bar, as written. A repeat signal's re-sent bracket is pending.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
