# #433078 Multi indicator Trend Following Strategy -> `fmz_433078_ssl_hybrid_macd_bb_session_volume_strength_5m_reversal`

- FMZ source id: 433078 (lineage).
- Source: https://www.fmz.com/strategy/433078 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 11:10:27). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent target from the fill, close-based stop in the signals |
| 2 | PASS | SSL-hybrid trend, MACD Bollinger continuation and session volume strength |
| 3 | PASS | No backtest header; bar size from the source's comment. |
| 4 | DONE | Qty = equity x leverage / close (leverage 1), 1 % of equity default, commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.01, 0.02] x `sl` [0.02, 0.03]: **4 trials**; EMA 30, channel 0.2, MACD 12 / 26 / BB 10 x 1, look-backs 4 / 1.

## Ambiguities resolved

- f_priorBarsSatisfied = the condition exactly N bars back (shadowed flag); session read in UTC; FREQ from the source's "//5 min" comment.
- Target from the fill (script: next bar). Volume = broker tick volume. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_hybrid"`.

## Marks

`none`
