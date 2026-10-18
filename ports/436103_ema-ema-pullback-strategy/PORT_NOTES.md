# #436103 EMA黄金交叉回调策略EMA-Pullback-Strategy -> `fmz_436103_ema_pullback_risk_bracket`

- FMZ source id: 436103 (lineage).
- Source: https://www.fmz.com/strategy/436103 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-21 11:48:54). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA structure and a risk-sized bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based, risk-capped quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ratio` [2.06, 3.0] x `risk_low` [0.008, 0.015]: **4 trials**; EMA 33 / 165 / 365 fixed.

## Ambiguities resolved

- Bracket re-based on the fill; risk from the pullback extreme; entry from flat. Opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback"`.

## Marks

`none`
