"""Stochastic RSI and Heikin-Ashi turn confluence in an SMA 100 / 50 / 20 trend, 1-hour bars: a new combined signal (a stochastic RSI cross up under 20 and an HA turn to green within 3 bars) in an up trend goes
long; the mirror outside an up trend goes short; a low under the previous 10-bar low closes a long, a high over the previous 10-bar high closes a short.
Port of FMZ strategy #439993 "Quantitative Support and Resistance Oscillation Strategy" (@sentenzal strategy).

FMZ source id: 439993

Source
    https://www.fmz.com/strategy/439993 (PineScript v4, FMZ last modified 2024-01-25 15:53:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-195), stoch RSI 3 / 3 / 14 / 14, 80 / 20; SMA 100 / 50 / 20; start 2017
    buy = a crossBuy and an HA buy (green after two non-green) in the last 3 bars;  signalBuy = buy and not buy[1] and not buy[2] and uptrend (sma100 < sma50 < sma20 and close > sma100);  sell / signalSell mirror (downtrend)
    close L when low < lowest(low, 10)[1];  close S when high > highest(high, 10)[1];  then entry L (signalBuy and uptrend), entry S (signalSell and not uptrend)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi candles are built from the module's own bars (same period). The closes are written
      before the entries: a long closed on a bar that also signals a long is reopened (it stays long);
      an opposite entry reverses. The start date covers the data (#436533). strategy.entry reverses:
      REVERSAL INTENDED. The size of 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic RSI, Heikin-Ashi turns, SMA trend and channel breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed size stored.
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

NAME = "fmz_439993_sentenzal_stochrsi_ha_trend"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_lengh": [100, 200],
    "oversold": [20, 30],
}
DEFAULT_PARAMS = {"sma_lengh": 100, "oversold": 20, "sma_lengh2": 50, "sma_lengh3": 20, "smooth_k": 3,
                  "smooth_d": 3, "length_rsi": 14, "length_stoch": 14, "dc_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _within3(x):
    return x | x.shift(1, fill_value=False) | x.shift(2, fill_value=False)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    r = _rsi(c, int(p["length_rsi"]))
    n = int(p["length_stoch"])
    ll, hh = r.rolling(n).min(), r.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100 * (r - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    os_ = float(p["oversold"])
    ob = 100 - os_
    cb = (k > d) & (k.shift(1) <= d.shift(1)) & (k < os_)
    cs = (k < d) & (k.shift(1) >= d.shift(1)) & (k > ob)
    hc = ((o + h + lo + c) / 4).to_numpy()
    ov = o.to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ho = np.full(m, np.nan)
    for i in range(m):
        ho[i] = (ov[i] + cv[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    pos_ha = pd.Series(hc >= ho, index=c.index)
    hb = pos_ha & ~pos_ha.shift(1, fill_value=True) & ~pos_ha.shift(2, fill_value=True)   # undefined history fails
    hs = ~pos_ha & pos_ha.shift(1, fill_value=False) & pos_ha.shift(2, fill_value=False)
    buy = _within3(cb) & _within3(hb)
    sell = _within3(cs) & _within3(hs)
    s1, s2, s3 = (c.rolling(int(p[kk])).mean() for kk in ("sma_lengh", "sma_lengh2", "sma_lengh3"))
    upt = (s1 < s2) & (s2 < s3) & (c > s1)
    dnt = (s1 > s2) & (s2 > s3) & (c < s1)
    b1, b2 = buy.shift(1, fill_value=False), buy.shift(2, fill_value=False)
    q1, q2 = sell.shift(1, fill_value=False), sell.shift(2, fill_value=False)
    sig_b = (buy & ~b1 & ~b2 & upt).to_numpy()
    sig_s = (sell & ~q1 & ~q2 & dnt & ~upt).to_numpy()
    dcn = int(p["dc_len"])
    xl = (lo.rolling(dcn).min().shift(1) > lo).to_numpy()
    xs = (h.rolling(dcn).max().shift(1) < h).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if sig_b[i]:
            new = 1
        elif sig_s[i]:
            new = -1
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
