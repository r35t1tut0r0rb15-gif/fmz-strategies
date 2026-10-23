"""A volume-weighted RSI (Wilder-style averages of volume x the close change over 100 bars) with a 100-bar relative volatility index state, hourly bars, long only: the volume RSI crossing over 50 while the RVI state is up goes long; the volume RSI crossing under 49 while the state is down closes; a 100 % target and a 20 % stop of the signal close also close.
Port of FMZ strategy #426389 "Cryptocurrency RSI Curve Tracking Strategy" (Crypto RSI + RVI Strategy).

FMZ source id: 426389

Source
    https://www.fmz.com/strategy/426389 (PineScript v4, FMZ last modified 2023-09-11 17:24:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 72-166), Period 100; BuyZone 49, SellZone 50; RVI 13 / 14 smoothing of stdev(close, 100); TP 1.0, SL 0.2 of the close (in ticks); risk 100, leverage 2.5
    rsi_v = 100 x WiMA(up x volume, 100) / (WiMA(up x volume) + WiMA(dn x volume));  nRes = 100 nU / (nU + nD);  pos = nRes < 49 ? -1 : nRes > 50 ? 1 : pos[1]
    long = crossover(rsi_v, 50) and pos == 1 -> entry long;  short = crossunder(rsi_v, 49) and pos == -1 -> close long
    exit("long_tp/sl", "long", profit = close x 1.0 / mintick, loss = close x 0.2 / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * WiMA starts from src / length on the first bar (nz of its own history), as written. The RVI sums
      start once stdev(close, 100) (population) exists. The exit distances are 100 % and 20 % of the
      LATEST close, re-sent every bar; the port fixes them at the signal close as fractions of the fill
      (mark trailing_stop_pending). The "short" exit id has no entry (the short entry is commented out).
      The open / close bookkeeping block only feeds plots. Long only. Stop module: portfolio_kwargs {}
      (driver D4). The equity x leverage quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close.
    2 generic: PASS, volume-weighted RSI with a volatility-direction state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 2.5 / open x risk / 100, 100 % of equity, capital 1000, commission 0.03 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted RSI (up / down close changes x volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426389_volume_weighted_rsi100_rvi_state_long_pct_bracket"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [100, 50],
    "sl": [0.2, 0.05],
}
DEFAULT_PARAMS = {"period": 100, "sl": 0.2, "tp": 1.0, "buy_zone": 49.0, "sell_zone": 50.0}


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


def _wima(x, n):
    """The source's WiMA: (src + nz(prev x (n - 1))) / n, from the first bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (v[i] + (0.0 if np.isnan(prev) else prev * (n - 1))) / n
        prev = out[i]
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["period"])
    d = c.diff()
    up = (d.abs() * v).where(d > 0, 0.0)
    dn = (d.abs() * v).where(d < 0, 0.0)
    upt, dnt = _wima(up, n), _wima(dn, n)
    rsi_v = 100 * (upt / (upt + dnt))
    sd = c.rolling(n).std(ddof=0).to_numpy(dtype=float)
    rise = (d > 0).to_numpy()
    m = len(sd)
    pos = np.zeros(m)
    nu = nd = np.nan
    pp = 0.0
    bz, sz = float(p["buy_zone"]), float(p["sell_zone"])
    for i in range(m):
        u_, d_ = (sd[i], 0.0) if rise[i] else (0.0, sd[i])
        nu = (13 * (0.0 if np.isnan(nu) else nu) + u_) / 14
        nd = (13 * (0.0 if np.isnan(nd) else nd) + d_) / 14
        nres = 100 * nu / (nu + nd) if (nu + nd) != 0 else np.nan
        pp = -1.0 if nres < bz else (1.0 if nres > sz else pp)
        pos[i] = pp
    pos_s = pd.Series(pos, index=c.index)
    long_ = (rsi_v > sz) & (rsi_v.shift(1) <= sz) & (pos_s == 1)
    short_ = (rsi_v < bz) & (rsi_v.shift(1) >= bz) & (pos_s == -1)
    return long_, short_


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, lx & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    sl_f, tp_f = float(p["sl"]) * k, float(p["tp"]) * k
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
