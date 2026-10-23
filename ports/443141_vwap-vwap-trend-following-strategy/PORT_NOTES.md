# #443141 基于VWAP的趋势跟随策略VWAP-Trend-Following-Strategy -> `fmz_443141_three_bar_ema200_vwap_trend_pct_brackets_2h`

- FMZ source id: 443141 (lineage).
- Source: https://www.fmz.com/strategy/443141 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-29 15:26:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed percent brackets from the fill |
| 2 | PASS | Three-bar trend / VWAP agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 90 % of equity, capital 100, commission 0.04 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_tp` [0.035, 0.02] x `long_sl` [0.014, 0.01]: **4 trials**; short TP 2.5 % / SL 0.9 %, EMA 200.

## Ambiguities resolved

- No reversal (side calls gated by the position); brackets followed in the signals. Volume = broker tick volume (VWAP). FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`coarse_bar_stop`
