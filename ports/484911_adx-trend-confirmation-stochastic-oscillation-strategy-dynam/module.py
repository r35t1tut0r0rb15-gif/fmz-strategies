"""Stochastic crosses at the extremes in a strong ADX trend, long only, broker days: with ADX 14 above 25, %K crossing
above %D below 20 goes long; with ADX above 25, %K crossing below %D above 80 closes the trade.
Port of FMZ strategy #484911 "趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators" (MY3 ADX+Stokastik).

FMZ source id: 484911

Source
    https://www.fmz.com/strategy/484911 (PineScript v5, FMZ last modified 2025-03-05 09:42:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 209-253), ADX 14 > 25, stochastic 14 / 3 / 3 (20 / 80)
    DI from rma of the directional moves over rma of the true range; adx = rma(100 x |DI+ - DI-| / (DI+ + DI-), 14)
    k = sma(stoch(close, high, low, 14), 3); d = sma(k, 3)
    buy = adx > 25 and crossover(k, d) and k < 20 -> entry long;  sell = adx > 25 and crossunder(k, d) and k > 80 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI as written (the first true range is na because close[1] is, so the smoothing starts on the second bar).
    * The two crosses cannot fall on one bar. Long only: opposite entries cannot occur.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX and a stochastic.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484911_adx_stoch_extreme_cross_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_threshold": [25.0, 20.0],
    "band": [20, 30],
}
DEFAULT_PARAMS = {"adx_period": 14, "adx_threshold": 25.0, "k_period": 14, "smooth_k": 3, "d_period": 3, "band": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["adx_period"])
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / atr, 100 * _rma(mdm, n) / atr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), n)
    kp = int(p["k_period"])
    ll, hh = lo.rolling(kp).min(), h.rolling(kp).max()
    st = 100 * (c - ll) / (hh - ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["d_period"])).mean()
    strong = adx > p["adx_threshold"]
    lo_b, hi_b = float(p["band"]), 100.0 - float(p["band"])
    long_e = (strong & (k > d) & (k.shift(1) <= d.shift(1)) & (k < lo_b)).astype(bool)
    long_x = (strong & (k < d) & (k.shift(1) >= d.shift(1)) & (k > hi_b)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
