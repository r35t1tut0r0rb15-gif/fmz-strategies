"""RSI 14 divergences after oversold / overbought, broker days: a regular or hidden bullish divergence at a confirmed RSI pivot low (5 / 5), with the RSI under 35 in the last 30 bars and under 50 now, goes
long; the bearish mirror (pivot high, over 70 in the last 30 bars, over 60 now) goes short; reversing; each trade has a 0.5 % stop and a 2 % target from the fill.
Port of FMZ strategy #438059 "基于RSI指标的多空反转策略RSI-Indicator-Based-Reversal-Strategy" (RSI OB/OS Divergence).

FMZ source id: 438059

Source
    https://www.fmz.com/strategy/438059 (PineScript v5, FMZ last modified 2024-01-08 16:47:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 180-364), RSI 14 on close; pivots 5 / 5, range 5-60; OB 70 (30 bars), OS 35 (30 bars); bear min 60, bull max 50; long and short SL 0.5 %, TP 2 %; dates 2016-2040
    plFound = pivotlow(rsi, 5, 5);  bull = low[5] < valuewhen(plFound, low[5], 1) and rsi[5] > valuewhen(plFound, rsi[5], 1) and barssince(plFound[1]) in 5..60 and plFound and lowest(rsi, 30) < 35 and rsi < 50
    hidden bull = higher price low with a lower RSI low;  bear / hidden bear mirror on pivot highs with highest(rsi, 30) > 70 and rsi > 60;  entry Bull / Bear;  exit(limit = avg x (1 +/- 2 %), stop = avg x (1 -/+ 0.5 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivots are strict on both sides (as #434470) and confirmed 5 bars later; the comparisons take
      the previous pivot's RSI and low (high). The bracket is sent from the first bar close inside the
      trade (one bar after the fill); the port fixes it at entry (sl_stop = 0.005, tp_stop = 0.02 of the
      fill). The date range covers the data. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, RSI pivots and divergences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438059_rsi_obos_divergence_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lb": [5, 3],
    "stop": [0.005, 0.01],
}
DEFAULT_PARAMS = {"lb": 5, "stop": 0.005, "take": 0.02, "rsi_len": 14, "range_lower": 5, "range_upper": 60,
                  "obvalue": 70.0, "oblookback": 30, "osvalue": 35.0, "oslookback": 30, "min_bear_rsi": 60.0,
                  "max_bull_rsi": 50.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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


def _pivot(x, left, right, low):
    """True at bar i when bar i - right is a strict pivot (both sides), known at bar i."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for i in range(left + right, m):
        p = i - right
        v = x[p]
        if np.isnan(v):
            continue
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if np.isnan(w).any():
            continue
        out[i] = (v < w).all() if low else (v > w).all()
    return out


def _divergences(osc, price, found, lb, lo_rng, hi_rng):
    """Regular (price lower, osc higher for lows) and hidden flags at bars where a pivot is found."""
    m = len(osc)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_o = last_p = np.nan
    last_bar = -1
    for i in range(m):
        if found[i]:
            o_now, p_now = osc[i - lb], price[i - lb]
            bars = i - last_bar - 1 if last_bar >= 0 else -1      # barssince(found[1])
            ok = last_bar >= 0 and lo_rng <= bars <= hi_rng
            reg[i] = ok and p_now < last_p and o_now > last_o
            hid[i] = ok and p_now > last_p and o_now < last_o
            last_o, last_p, last_bar = o_now, p_now, i
    return reg, hid


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    osc_s = _rsi(c, int(p["rsi_len"]))
    osc = osc_s.to_numpy()
    lb = int(p["lb"])
    pl = _pivot(osc, lb, lb, True)
    ph = _pivot(osc, lb, lb, False)
    lr, hr = int(p["range_lower"]), int(p["range_upper"])
    bull, hbull = _divergences(osc, lo.to_numpy(dtype=float), pl, lb, lr, hr)
    bear_n, hbear_n = _divergences(-osc, -h.to_numpy(dtype=float), ph, lb, lr, hr)
    os_ok = (osc_s.rolling(int(p["oslookback"])).min() < float(p["osvalue"])).to_numpy() & (osc < float(p["max_bull_rsi"]))
    ob_ok = (osc_s.rolling(int(p["oblookback"])).max() > float(p["obvalue"])).to_numpy() & (osc > float(p["min_bear_rsi"]))
    return (bull | hbull) & os_ok, (bear_n | hbear_n) & ob_ok


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]), "tp_stop": float(p["take"])}


def portfolio_kwargs(**params):
    return {}
