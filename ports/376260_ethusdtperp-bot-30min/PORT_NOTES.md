# #376260 ETHUSDTPERP BOT 30min -> `fmz_376260_adx_mn16_volume_hull_rsi_momentum_dosc_pct_bracket_reversal`

- FMZ source id: 376260 (lineage).
- Source: https://www.fmz.com/strategy/376260 (PineScript v4, author a624587332, FMZ last
  modified 2022-08-02 23:47:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | ADX direction with volume and RSI-momentum confirmation |
| 3 | PASS | No exchange header. |
| 4 | DONE | 100 % of equity, capital 10000 and commission 0.075 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rvol_trigger` [1.2, 1.0] x `th` [13.5, 20.0]: **4 trials**; TP 1.6 %, SL 4.3 %, the other settings as written.

## Ambiguities resolved

- Bar size from the title (30min). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`none`
