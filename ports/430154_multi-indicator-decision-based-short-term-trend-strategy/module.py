"""A stochastic RSI 14 / 14 / 3 / 3 cross and a candle crossing the daily VWAP of ohlc4 (in that or the previous bar, both one bar back), a close crossing a Fibonacci daily pivot or support a bar back, and two candles in the trade's direction, hourly bars: the bullish set goes long, the bearish set goes short; a close 1 % beyond the entry closes; reversing.
Port of FMZ strategy #430154 "Multi indicator Decision Based Short Term Trend Strategy" (EmperorBTC's VWAP Strategy).

FMZ source id: 430154

Source
    https://www.fmz.com/strategy/430154 (PineScript v4, FMZ last modified 2023-10-25 15:31:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 185-353), pivots Fibonacci from the previous day; VWAP period D of ohlc4; stoch RSI 14 / 14, K 3, D 3; TP 1 % (close test); direction L&S
    longCond = (sRsiCrossUp or [1])[1] and (vwapCrossUp or [1])[1] and pivotPointCrossedUp[1] and close[1] > open[1] and close > open -> entry VWAP long;  shortCond mirror -> entry VWAP short
    exitTp = long and close > avg x 1.01 or short and close < avg x 0.99 -> close VWAP

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day is the UTC calendar day (time("D") of the header exchange; fixed UTC, no DST) for both the
      VWAP reset and the previous day's high / low / close behind the pivots. pivotPointCrossedDown tests
      the SUPPORTS and the pivot (not the resistances), as written. The take-profit is a close test against
      the fill; the close acts only on a position the bar's entries leave unchanged. The date range
      (2017 .. 2050) is dropped. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target.
    2 generic: PASS, pivot / VWAP / stochastic-RSI confluence.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the daily VWAP of ohlc4; exchange volume to be compared later (Austin, 2026-10-23).
Session open: day start 00:00 UTC (time("D") of the header exchange; fixed UTC, no DST) for the VWAP and the pivots.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430154_fib_pivot_cross_daily_vwap_stoch_rsi_cross_close_tp_reversal"
FAMILY = "vwap_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "take_profit": [0.01, 0.02],
    "length_rsi": [14, 21],
}
DEFAULT_PARAMS = {"take_profit": 0.01, "length_rsi": 14, "length_stoch": 14, "smooth_k": 3, "smooth_d": 3}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    ix = c.index
    day = pd.Series(ix.tz_convert("UTC").normalize(), index=ix)
    dly = pd.DataFrame({"h": h, "l": lo, "c": c, "d": day}).groupby("d").agg({"h": "max", "l": "min", "c": "last"})
    prev = dly.shift(1)                                   # the previous completed UTC day
    ph, pl, pcl = (pd.Series(prev[k].reindex(day).to_numpy(), index=ix) for k in ("h", "l", "c"))
    pp = (ph + pl + pcl) / 3
    rng = ph - pl
    s1, s2, s3 = pp - 0.382 * rng, pp - 0.618 * rng, pp - rng
    pp_up = ((lo < s3) & (c > s3)) | ((lo < s2) & (c > s2)) | ((lo < s1) & (c > s1)) | ((lo < pp) & (c > pp))
    pp_dn = ((h > s3) & (c < s3)) | ((h > s2) & (c < s2)) | ((h > s1) & (c < s1)) | ((h > pp) & (c < pp))
    ohlc4 = (o + h + lo + c) / 4
    vw = pd.Series(((ohlc4 * v).groupby(day.to_numpy()).cumsum() / v.groupby(day.to_numpy()).cumsum()).to_numpy(), index=ix)
    vw_up = (lo < vw) & (vw < h) & (c > o)
    vw_dn = (h > vw) & (vw > lo) & (c < o)
    d_ = c.diff()
    n = int(p["length_rsi"])
    r = 100 - 100 / (1 + _rma(d_.clip(lower=0), n) / _rma((-d_).clip(lower=0), n))
    ns = int(p["length_stoch"])
    st = 100 * (r - r.rolling(ns).min()) / (r.rolling(ns).max() - r.rolling(ns).min()).replace(0.0, np.nan)
    k = st.rolling(int(p["smooth_k"])).mean()
    dd = k.rolling(int(p["smooth_d"])).mean()
    sr_up = (k.shift(1) < dd.shift(1)) & (k > dd)
    sr_dn = (k.shift(1) > dd.shift(1)) & (k < dd)
    either = lambda x: (x | x.shift(1, fill_value=False)).shift(1, fill_value=False)
    lc = (either(sr_up) & either(vw_up) & pp_up.shift(1, fill_value=False) & (c.shift(1) > o.shift(1)) & (c > o)).to_numpy()
    sc = (either(sr_dn) & either(vw_dn) & pp_dn.shift(1, fill_value=False) & (c.shift(1) < o.shift(1)) & (c < o)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp = float(p["take_profit"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, avg = 0, np.nan
    for i in range(m):
        old = pos
        tgt = old
        if lc[i]:
            tgt = 1
        if sc[i]:
            tgt = -1
        if tgt == old == 1 and cv[i] > avg * (1 + tp):
            tgt = 0
        elif tgt == old == -1 and cv[i] < avg * (1 - tp):
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
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
