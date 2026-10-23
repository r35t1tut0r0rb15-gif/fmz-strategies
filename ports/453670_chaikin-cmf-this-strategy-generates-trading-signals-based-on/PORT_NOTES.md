# #453670 基于Chaikin资金流量CMF指标策略This-strategy-generates-trading-signals-based-on-the-Chaikin-Money-Flow-CMF -> `fmz_453670_cmf200_ema80_160_cross_delayed_pct_bracket_reversal`

- FMZ source id: 453670 (lineage).
- Source: https://www.fmz.com/strategy/453670 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 17:05:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 3 % / 5 % bracket from the fill |
| 2 | PASS | Money-flow EMA crossings, entered one bar later |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmf_period` [200, 50] x `ema_fast` [80, 20]: **4 trials**; EMA slow 160, SL 3 %, TP 5 %.

## Ambiguities resolved

- Entry one bar after the crossing; doji bars count 0 in the CMF. Volume = broker tick volume (CMF). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`coarse_bar_stop`
