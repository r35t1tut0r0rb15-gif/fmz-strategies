"""The UT Bot ATR 6 x 2 trailing line state, a Schaff trend cycle (EMA 27 / 50, cycle 80, factor 0.5) turning up under 25 (down over 75) and the Hull 55 above (below) its value two bars back, hourly bars: all bullish goes long when not long, all bearish goes short when not short; a close 15 % against the entry closes, with a 100 % target from the entry; reversing.
Port of FMZ strategy #428580 "基于Hull-MA与STC指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Hull-MA-and-STC-Indicator" (Strategy Myth-Busting #1 - UT Bot+STC+Hull+ [MYN]).

FMZ source id: 428580

Source
    https://www.fmz.com/strategy/428580 (PineScript v5, FMZ last modified 2023-10-07 10:20:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 208-493), UT Bot key 2, ATR 6 (close); STC 80 / 27 / 50, AAA 0.5; Hull Hma 55; TP 1-4 at 100 %; SL 15 % (close test); template of #426563
    UTBotBuyZone = the last UT buy (close crossing over the trailing line) is newer than the last sell;  STC rising and < 25;  hull(close, 55) > hull[2]
    long condition and not in a long -> entry Long;  short mirror -> entry Short;  exit(TP1..4, profit = 100 % of the avg price);  close < avg x 0.85 -> close Long (short mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The UT Bot line and state are QuantNomad's, as written (Heikin-Ashi source off). The STC keeps its
      previous value while a window's range is 0 and starts from 0 (var). The Hull length halves are taken
      as integers and the root is rounded (math.round, as written). The four targets are 100 % with 100 % of
      the position each: the first closes it all, a scalar 1.0 of the fill. The closes act only on a
      position the bar's entries leave unchanged. The volume only appears in an alert text, so it does not
      reach the orders: ported as not using volume (check 8). The 2019 .. 2030 window is dropped.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The equity x leverage contracts are
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop; target from the fill.
    2 generic: PASS, ATR trailing state with Schaff cycle and Hull trend agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the author's 2019 .. 2030 window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428580_ut_bot_stc_hull55_agreement_close_stop_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "key": [2.0, 1.0],
    "hull_len": [55, 100],
}
DEFAULT_PARAMS = {"key": 2.0, "hull_len": 55, "atr_period": 6, "stc_len": 80, "stc_fast": 27, "stc_slow": 50,
                  "stc_factor": 0.5, "sl": 0.15, "tp": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _ut_bot(c, atr, key):
    """QuantNomad's UT Bot trailing line; buy / sell when the close crosses it."""
    s = c.to_numpy(dtype=float)
    nl = (key * atr).to_numpy(dtype=float)
    m = len(s)
    ts = np.zeros(m)
    prev = 0.0
    for i in range(m):
        s1 = s[i - 1] if i else np.nan
        if s[i] > prev and s1 > prev:
            t = max(prev, s[i] - nl[i])
        elif s[i] < prev and s1 < prev:
            t = min(prev, s[i] + nl[i])
        else:
            t = s[i] - nl[i] if s[i] > prev else s[i] + nl[i]
        ts[i] = t
        prev = 0.0 if np.isnan(t) else t
    tss = pd.Series(ts, index=c.index)
    above = (c > tss) & (c.shift(1) <= tss.shift(1))
    below = (tss > c) & (tss.shift(1) <= c.shift(1))
    return (c > tss) & above, (c < tss) & below


def _stc(c, n, fast, slow, f):
    """The source's Schaff trend cycle (var state from 0, previous value kept on a flat window)."""
    macd = (c.ewm(span=fast, adjust=False).mean() - c.ewm(span=slow, adjust=False).mean()).to_numpy()
    m = len(macd)

    def roll_lo_hi(x):
        s = pd.Series(x)
        return s.rolling(n).min().to_numpy(), s.rolling(n).max().to_numpy()

    lo1, hi1 = roll_lo_hi(macd)
    ccc = np.zeros(m)
    ddd = np.zeros(m)
    pc, pd_ = 0.0, np.nan
    for i in range(m):
        rng = hi1[i] - lo1[i]
        pc = (macd[i] - lo1[i]) / rng * 100 if rng > 0 else pc
        ccc[i] = pc
        pd_ = pc if np.isnan(pd_) else pd_ + f * (pc - pd_)
        ddd[i] = pd_
    lo2, hi2 = roll_lo_hi(ddd)
    out = np.zeros(m)
    p6, pe = 0.0, np.nan
    for i in range(m):
        rng = hi2[i] - lo2[i]
        p6 = (ddd[i] - lo2[i]) / rng * 100 if rng > 0 else p6
        pe = p6 if np.isnan(pe) else pe + f * (p6 - pe)
        out[i] = pe
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    buy, sell = _ut_bot(c, _rma(tr, int(p["atr_period"])), float(p["key"]))
    t = np.arange(len(c))
    lb = np.maximum.accumulate(np.where(buy.to_numpy(), t + 1, 0))
    ls = np.maximum.accumulate(np.where(sell.to_numpy(), t + 1, 0))
    zone_b, zone_s = lb > ls, ls > lb
    stc = _stc(c, int(p["stc_len"]), int(p["stc_fast"]), int(p["stc_slow"]), float(p["stc_factor"]))
    n = int(p["hull_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    lcond = ((stc > stc.shift(1)) & (stc < 25) & (hull > hull.shift(2))).to_numpy() & zone_b
    scond = ((stc < stc.shift(1)) & (stc > 75) & ~(hull > hull.shift(2))).to_numpy() & zone_s   # HullRed = not green
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sl = float(p["sl"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, avg = 0, np.nan
    for i in range(m):
        old = pos
        tgt = old
        if lcond[i] and old != 1:
            tgt = 1
        if scond[i] and old != -1:
            tgt = -1
        if tgt == old == 1 and cv[i] < avg * (1 - sl):
            tgt = 0
        elif tgt == old == -1 and cv[i] > avg * (1 + sl):
            tgt = 0
        if tgt != old and tgt != 0 and i + 1 < m:
            avg = ov[i + 1]
        pos = tgt
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
