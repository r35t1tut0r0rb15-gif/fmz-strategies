# #440507 基于renko股票日内低点回撤的stock日内交易策略Intraday-Trading-Strategy-for-Stocks-Based-on-Renko-Low-Point-Retracement -> `fmz_440507_vix_fix_spike_end_long`

- FMZ source id: 440507 (lineage).
- Source: https://www.fmz.com/strategy/440507 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-31 10:53:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Vix Fix and its bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd` [22, 14] x `ph` [0.85, 0.9]: **4 trials**; BB 20 / 2 and the 50-bar look-back fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`none`
