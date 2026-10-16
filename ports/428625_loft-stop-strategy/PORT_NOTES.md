# #428625 Loft Stop Strategy -> `fmz_428625_kalman_loft_stop_flip`

- FMZ source id: 428625 (lineage).
- Source: https://www.fmz.com/strategy/428625 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-07 16:11:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; take-profit fixed at entry. |
| 2 | PASS | Percentages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Exit settings quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_max` [2, 4] x `tp` [1.5, 3]: **4 trials**; defaults 2 / 1.5 (the source's); gain 1, final approach 0.5 %, step 0.005 fixed.

## Ambiguities resolved

- The "loft stop" is a signal line on the Kalman value: each flip is an entry the other way (reversal). The stop-loss input is 0 (no stop); take-profit `tp_stop` 0.015.
- After a take-profit the next entry waits for the next flip (stopped-out flags). Date window open; both sides on.
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. Stops on 2-hour bars: mark `coarse_bar_stop`. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "kalman_trend"`.

## Marks

`coarse_bar_stop`
