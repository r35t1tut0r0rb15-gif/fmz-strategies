"""Keltner, volatility-stop and Waddah Attar confluence, 1-hour bars: the close above the Keltner upper line (EMA 200 of hlc3 plus 5 x EMA 200 of the range) and above the volatility stop with a Waddah
Attar up-explosion goes long; the close crossing back under the Keltner line or the stop closes; mirrored for shorts; reversing.
Port of FMZ strategy #440309 "Cross Cycle Arbitrage Strategy Based on Multiple Indicators" (QuarryLake).

FMZ source id: 440309

Source
    https://www.fmz.com/strategy/440309 (PineScript v4, FMZ last modified 2024-01-29 11:10:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-240), Keltner 200 / 5; volatility stop ATR 3 x 1.5; WAE sensitivity 150, EMA 20 / 40, BB 20 / 2, dead zone rma(tr, 100) x 3.7
    long = close > KC upper and close > vstop and trendUp > dead zone and trendUp > BB width;  close Long on crossunder(close, KC upper) or crossunder(close, vstop)
    short = close < KC lower and close < vstop and trendDown > dead zone and trendDown > BB width;  close Short on crossover(close, KC lower) or crossover(close, vstop);  order: entry Long, close Long, entry Short, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * trendUp = 150 x the one-bar change of MACD(20, 40) when positive (trendDown when negative); the BB
      width is upper minus lower (population deviation); the dead zone is 0 until rma(tr, 100) exists.
      The volatility stop is the script's ratchet, with its nz(..) starts (the running minimum starts
      at 0); its first ATR bars are approximate. A close acts only on the position held: a close written
      after a reversing entry leaves the reversal standing (as #438020). strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner line, volatility stop and MACD-change explosion.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (a Kelly note in a comment only).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440309_quarrylake_keltner_vstop_wae"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kc_mult": [5, 2],
    "sensitivity": [150, 300],
}
DEFAULT_PARAMS = {"kc_mult": 5, "sensitivity": 150, "kc_period": 200, "vstop_len": 3, "vstop_mult": 1.5,
                  "fast": 20, "slow": 40, "bb_len": 20, "bb_mult": 2.0}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def _vstop(c, atr, k):
    """The script's volatility stop, with its nz() starts (max and min from 0, uptrend true)."""
    cv, av = c.to_numpy(dtype=float), atr.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    mx_p, mn_p, up_p, vs_p = 0.0, 0.0, True, 0.0
    for i in range(len(cv)):
        ci, a = cv[i], av[i]
        mx1, mn1 = max(mx_p, ci), min(mn_p, ci)
        st = mx1 - k * a if up_p else mn1 + k * a
        vs1 = np.nan if np.isnan(st) else (max(vs_p, st) if up_p else min(vs_p, st))
        is_up = (not np.isnan(vs1)) and ci - vs1 >= 0
        ch = is_up != up_p
        mx, mn = (ci, ci) if ch else (mx1, mn1)
        vs = ((mx - k * a) if is_up else (mn + k * a)) if ch else vs1
        out[i] = vs
        mx_p, mn_p, up_p = mx, mn, is_up
        vs_p = 0.0 if np.isnan(vs) else vs
    return pd.Series(out, index=c.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kc_period"])
    mid = ((h + lo + c) / 3).ewm(span=n, adjust=False).mean()
    mv = (h - lo).ewm(span=n, adjust=False).mean() * float(p["kc_mult"])
    up, dn = mid + mv, mid - mv
    tr = _tr(bars_df)
    vs = _vstop(c, _rma(tr, int(p["vstop_len"])), float(p["vstop_mult"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    t1 = (macd - macd.shift(1)) * float(p["sensitivity"])
    e1 = 2 * float(p["bb_mult"]) * c.rolling(int(p["bb_len"])).std(ddof=0)
    dz = _rma(tr, 100).fillna(0.0) * 3.7
    t_up, t_dn = t1.clip(lower=0), (-t1).clip(lower=0)
    wl = (t_up > 0) & (t_up > dz) & (t_up > e1)
    ws = (t_dn > 0) & (t_dn > dz) & (t_dn > e1)

    def xu(x, y):
        return (x < y) & (x.shift(1) >= y.shift(1))

    L = ((c > up) & (c > vs) & wl).to_numpy()
    LX = (xu(c, up) | xu(c, vs)).to_numpy()
    S = ((c < dn) & (c < vs) & ws).to_numpy()
    SX = (xu(dn, c) | xu(vs, c)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if LX[i] and pos == 1 and new == 1:
            new = 0
        if S[i]:
            new = -1
        if SX[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
