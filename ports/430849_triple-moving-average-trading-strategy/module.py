"""Triple SMA 50 / 100 / 200 crosses (BigBitsIO), 1-hour bars, long only from flat: a cross-up of any pair (50 / 100,
50 / 200, 100 / 200) goes long with a 30 % target and a 15 % stop; the cross-down of the pair that opened the trade
closes it.
Port of FMZ strategy #430849 "Triple Moving Average Trading Strategy" (Triple Many Moving Averages).

FMZ source id: 430849

Source
    https://www.fmz.com/strategy/430849 (PineScript v4, FMZ last modified 2023-11-02 14:47:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 179-471), SMA 50 / 100 / 200 (current resolution), TP 30 %, SL 15 % of the close in ticks, pyramiding 1
    crossover(MA1, MA2) -> entry "1 over 2" + exit("profit or loss", "1 over 2", profit, loss); crossunder -> close "1 over 2"
    crossover(MA1, MA3) -> entry "1 over 3" (same exit id); crossunder -> close "1 over 3"
    crossover(MA2, MA3) -> entry "2 over 3" (same exit id); crossunder -> close "2 over 3"
    profit = close x 30 % / mintick, loss = close x 15 % / mintick

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 1: only one long at a time; the first cross on a flat book (in source order) names the
      trade, and only that pair's cross-down closes it. "Flat" follows the house bracket on bars.
    * The bracket distances are 30 % / 15 % of the signal close (tp 0.30, sl 0.15 of the fill). The
      exit id is shared, so a later cross-up of another pair while long re-binds it to an entry that
      never fills and the open trade loses its bracket in the source: not modelled (each trade keeps
      its bracket; stated approximation).
    * The forecasts and ribbons only plot. Long only; Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (the shared-id re-binding approximated).
    2 generic: PASS, moving-average crosses and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430849 (2 members, best partner #435959, Jaccard 0.757); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430849_triple_sma_crosses_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [30.0, 10.0],
    "sl_pct": [15.0, 5.0],
}
DEFAULT_PARAMS = {"ma1": 50, "ma2": 100, "ma3": 200, "tp_pct": 30.0, "sl_pct": 15.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    c = bars_df["close"]
    m1, m2, m3 = (c.rolling(int(p[k])).mean() for k in ("ma1", "ma2", "ma3"))
    pairs = [(m1, m2), (m1, m3), (m2, m3)]
    xo = [((a > b) & (a.shift(1) <= b.shift(1))).to_numpy() for a, b in pairs]
    xu = [((a < b) & (a.shift(1) >= b.shift(1))).to_numpy() for a, b in pairs]
    s_, t_ = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, oid = 0, -1, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_):
                pos, oid = 0, -1
        if pos == 1 and i > entry_i - 1 and xu[oid][i]:
            lx[i], pos, oid = True, 0, -1
            continue
        if pos == 0:
            for k in range(3):
                if xo[k][i]:
                    le[i], pos, entry_i, oid = True, 1, i + 1, k
                    break
    return le, lx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
