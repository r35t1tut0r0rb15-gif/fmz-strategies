"""Supertrend, stochastic cross and four-EMA trend, 1-minute bars, from flat: with EMA 25 > 50 and 100 > 200 and the Supertrend
up, a %K cross up through %D goes long with the stop at the swing low since the last cross and a target 1.5 times that
distance; the mirror goes short.
Port of FMZ strategy #435266 "Momentum Breakout and Trend Following Combination Strategy" (Supertrend + Stoch Strategy).

FMZ source id: 435266

Source
    https://www.fmz.com/strategy/435266 (PineScript v4, FMZ last modified 2023-12-13 16:41:25).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 180-253), EMA 25 / 50 / 100 / 200; supertrend(3, 10); stoch 8, %K smoothing 3, %D 3; P/L 1.5; loss 1 % (sizing)
    edge = crossover(k, d) ? high : crossunder(k, d) ? low : k > d ? max(edge[1], high) : k < d ? min(edge[1], low) : edge[1]
    flat and ema1 > ema2 and ema3 > ema4 and supertrend up and crossover(k, d) -> stop = edge[1], take = close + (close - stop) pl, entry long, exit(limit = take, stop = stop);  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fraction of the fill price, with the distance from the signal bar's close:
      sl_stop = |close - edge[1]| / close, tp_stop = P/L x sl_stop (shifted one bar inside stops(),
      re-based on the fill). A signal whose stop is not beyond the close places no entry. The lot size
      (1 % risk) is sizing.
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot
      occur. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-minute bars: not coarse.
      FREQ = "1min" from the backtest header. Supertrend as Pine's built-in (the %K is stoch(close,
      high, low) smoothed).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, average trend, supertrend, stochastic and swing stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435266_supertrend_stoch_swing_bracket"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pl": [1.5, 2.0],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"pl": 1.5, "factor": 3.0, "atr_len": 10, "k_len": 8, "k_smooth": 3, "d_smooth": 3,
                  "e1": 25, "e2": 50, "e3": 100, "e4": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _direction(h, lo, c, factor, n):
    """Direction of Pine's built-in supertrend(factor, atrPeriod): -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    dr = _direction(h, lo, c, float(p["factor"]), int(p["atr_len"]))
    n = int(p["k_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - ll) / (hh - ll)
    k = raw.rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    xo = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    xu = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    kv, dv = k.to_numpy(), d.to_numpy()
    hv, lv, cv, ov = (x.to_numpy(dtype=float) for x in (h, lo, c, o))
    m = len(cv)
    edge = np.zeros(m)
    for i in range(m):
        e1 = edge[i - 1] if i > 0 else 0.0
        if xo[i]:
            edge[i] = hv[i]
        elif xu[i]:
            edge[i] = lv[i]
        elif kv[i] > dv[i]:
            edge[i] = max(e1, hv[i])
        elif kv[i] < dv[i]:
            edge[i] = min(e1, lv[i])
        else:
            edge[i] = e1
    e1_, e2_, e3_, e4_ = (c.ewm(span=int(p[x]), adjust=False).mean() for x in ("e1", "e2", "e3", "e4"))
    up = ((e1_ > e2_) & (e3_ > e4_)).to_numpy()
    dn = ((e1_ < e2_) & (e3_ < e4_)).to_numpy()
    lc = up & (dr < 0) & xo
    sc = dn & (dr > 0) & xu
    pl = float(p["pl"])
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + pl * s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - pl * s_)):
                pos = 0
        if pos == 0 and i > 0:
            if lc[i] and cv[i] - edge[i - 1] > 0:
                le[i], pos, ei, s_ = True, 1, i + 1, (cv[i] - edge[i - 1]) / cv[i]
                sl[i] = s_
            elif sc[i] and edge[i - 1] - cv[i] > 0:
                se[i], pos, ei, s_ = True, -1, i + 1, (edge[i - 1] - cv[i]) / cv[i]
                sl[i] = s_
    return le, se, sl, sl * pl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
