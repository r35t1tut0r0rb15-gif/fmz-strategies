"""Stochastic(14, 3, 3) crossings at the extremes, 4-hour bars: %K crossing over %D under 20 goes long, crossing under above 80 goes short; a crossing back the other way at the opposite side closes; a
fixed target and stop from the entry (tick distances, re-expressed as ATR multiples); reversing.
Port of FMZ strategy #442556 "Dual Moving Average Crossover Strategy with Stop Loss and Take Profit" (Strategy alerts workaround).

FMZ source id: 442556

Source
    https://www.fmz.com/strategy/442556 (PineScript v5, FMZ last modified 2024-02-22 17:30:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-147), stochastic 14, K SMA 3, D SMA 3; stop 60, target 120 ticks
    crossover(k, d) and k < 20 -> entry Buy;  crossunder(k, d) and k > 80 -> entry Sell;  exit(loss = 60, profit = 120) for each id
    crossunder(k, d) and k <= 80 -> close Buy;  crossover(k, d) and k >= 20 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 60 / 120-tick stop and target are 6 / 12 price units at mintick 0.1 on the BTC
      reading; as ATR multiples at the 4-hour ATR(14) reading of about 400, a stop of 0.015 ATR and a
      target of 0.03 ATR of the signal bar, shifted one bar inside stops() and re-based on the fill.
      Ported in call order with one position at a time; each close acts only on its own held id. The
      alert messages are display. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. No sizing code.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442556 (2 members, best partner #444005, Jaccard 0.830); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442556_stoch_extreme_cross_atr_bracket"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 9],
    "tp_atr": [0.03, 1.0],
}
DEFAULT_PARAMS = {"length": 14, "tp_atr": 0.03, "sl_atr": 0.015, "atr_len": 14, "lower": 20, "upper": 80}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(3).mean()
    d = k.rolling(3).mean()
    co = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    cu = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    kv = k.to_numpy()
    lw, up = float(p["lower"]), float(p["upper"])
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov, hv, lv = bars_df["open"].to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 >= m or np.isnan(sl[i]):
            continue
        if co[i] and kv[i] < lw and pos != 1:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
        elif cu[i] and kv[i] > up and pos != -1:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
        elif cu[i] and kv[i] <= up and pos == 1 and i >= entry_i:
            lx[i], pos = True, 0
        elif co[i] and kv[i] >= lw and pos == -1 and i >= entry_i:
            sx[i], pos = True, 0
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
