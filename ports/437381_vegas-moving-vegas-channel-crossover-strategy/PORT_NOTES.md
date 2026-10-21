# #437381 移動的Vegas通道穿越策略Moving-Vegas-Channel-Crossover-Strategy -> `fmz_437381_vegas_tunnel_setups`

- FMZ source id: 437381 (lineage).
- Source: https://www.fmz.com/strategy/437381 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-02 10:53:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA tunnel, MACD sign, Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The per-setup quantities stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 30] x `bb_mult` [2.0, 2.5]: **4 trials**; every EMA length fixed.

## Ambiguities resolved

- One position at a time; exits by the setup that holds it; call-order fills. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
