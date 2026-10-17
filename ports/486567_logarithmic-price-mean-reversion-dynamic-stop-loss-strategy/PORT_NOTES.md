# #486567 对数价格均值回归动态止损策略-Logarithmic-Price-Mean-Reversion-Dynamic-Stop-Loss-Strategy -> `fmz_486567_log_zscore_reversion_vol_stop`

- FMZ source id: 486567 (lineage).
- Source: https://www.fmz.com/strategy/486567 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-14 09:39:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked exits. |
| 2 | PASS | A z-score of log prices. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [7, 14] x `z_entry` [1.825, 1.5]: **4 trials**; defaults 7 / 1.825 (the source's, symmetric for both sides);
stop z 2.125 fixed.

## Ambiguities resolved

- The take profit (the rolling mean) and the volatility-adjusted stop are close-checked: exit signals at the next
  open (rule 3). The script's position string gates entries (only from flat) and tracks the position; a trade that
  would close on its own entry bar (not possible with these levels) emits nothing. Opposite entries cannot occur.
  Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_mean_reversion"`.

## Marks

`none`
