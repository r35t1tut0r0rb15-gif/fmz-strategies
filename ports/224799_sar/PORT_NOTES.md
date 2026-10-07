# #224799 SAR抛物线转向指标 -> `fmz_224799_parabolic_sar_side`

- Source: https://www.fmz.com/strategy/224799 (JavaScript, author 韬奋量化, FMZ last modified
  2021-11-02 10:53:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar every 5 s; the port evaluates on completed bars. |
| 2 | PASS | SAR is built from the bars. |
| 3 | PASS (screen: REVIEW) | Quarterly / XBTUSD contract and 1x margin are venue set-up only. |
| 4 | DONE | Fixed `Amount`, ticker order prices -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Built from #193609's template (different indicator). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`acceleration` [0.01, 0.02, 0.03] x `maximum` [0.1, 0.2, 0.3] = **9 trials**.

## Ambiguities resolved

- SAR follows TA-Lib's algorithm (talib.SAR in the source), including the start direction from
  the first bar pair's minus-DM.
- Close-then-open on consecutive polls of one bar = a one-bar reversal.
- `FREQ = "1h"`: the code's `GetRecords(time_interval)` with the argument default 3600 s.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
