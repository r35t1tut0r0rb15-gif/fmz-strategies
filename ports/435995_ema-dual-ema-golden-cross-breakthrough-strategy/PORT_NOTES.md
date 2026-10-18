# #435995 双EMA黄金交叉突破策略Dual-EMA-Golden-Cross-Breakthrough-Strategy -> `fmz_435995_zlema_open_cross_session`

- FMZ source id: 435995 (lineage).
- Source: https://www.fmz.com/strategy/435995 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-20 16:34:58). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | ADAPT | Pip distances -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trade size and the pip inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435995. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_frac` [0.0055, 0.01] x `sl_frac` [0.0022, 0.005]: **4 trials**; ZLEMA 5 / 34 and the session fixed.

## Ambiguities resolved

- Session in UTC; stale apex / entry variables as in the script; pip distances -> fractions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
