"""EMA 11 / 50 crossings with the stochastic-RSI K over (under) D, 1-minute bars, long only: the up-cross with K over D goes long, the down-cross with K under D closes.
Port of FMZ strategy #490517 "多重确认变动平均趋势与随机RSI动量交易策略-Multi-Confirmation-EMA-Trend-and-Stochastic-RSI-Momentum-Trading-Strategy" (Haze EMA Signal).

FMZ source id: 490517

Source
    https://www.fmz.com/strategy/490517 (PineScript v6, FMZ last modified 2025-04-14 11:25:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 211-251), EMA 11 / 50; Stoch RSI 10, K 15, D 7; 100 % of equity
    crossover(ema11, ema50) and k > d -> entry Buy;  crossunder(ema11, ema50) and k < d -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stochastic RSI is stoch(rsi10, rsi10, rsi10, 10) smoothed by SMA 15 (K) and SMA 7 (D). Long only.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a stochastic-RSI side filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490517_ema11_50_cross_stochrsi_side_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fastLength": [11, 20],
    "slowLength": [50, 100],
}
DEFAULT_PARAMS = {"fastLength": 11, "slowLength": 50, "stochLength": 10, "kLength": 15, "dLength": 7}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fastLength"]), adjust=False).mean()
    s = c.ewm(span=int(p["slowLength"]), adjust=False).mean()
    n = int(p["stochLength"])
    r = _rsi(c, n)
    lo_, hi_ = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - lo_) / (hi_ - lo_).where(hi_ > lo_)
    k = st.rolling(int(p["kLength"])).mean()
    d = k.rolling(int(p["dLength"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (k > d)
    lx = (f < s) & (f.shift(1) >= s.shift(1)) & (k < d)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
