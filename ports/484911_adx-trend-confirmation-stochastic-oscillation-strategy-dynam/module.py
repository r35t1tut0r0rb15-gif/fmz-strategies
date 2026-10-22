"""Stochastic 14 / 3 / 3 K-D crossings in the extremes while a hand-built ADX 14 is over 25, broker days, long only: an up-cross under 20 goes long, a down-cross over 80 closes.
Port of FMZ strategy #484911 "趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators" (MY3 ADX+Stokastik).

FMZ source id: 484911

Source
    https://www.fmz.com/strategy/484911 (PineScript v5, FMZ last modified 2025-03-05 09:42:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 205-266), ADX 14 (hand-built, Wilder smoothing), threshold 25; Stochastic 14 / 3 / 3, levels 80 / 20; 10 % of equity, capital 10000
    adx > 25 and crossover(k, d) and k < 20 -> entry Long;  adx > 25 and crossunder(k, d) and k > 80 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is Wilder's, built by hand as written (the true range reads close[1], na on the first bar).
      Long only. The 10 % of equity size and the capital are sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stochastic extreme crossings with an ADX filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484911_stoch14_kd_cross_extremes_adx25_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_threshold": [25.0, 20.0],
    "stoch_k_period": [14, 9],
}
DEFAULT_PARAMS = {"adx_threshold": 25.0, "stoch_k_period": 14, "adx_period": 14, "stoch_smooth_k": 3,
                  "stoch_d_period": 3, "overbought": 80, "oversold": 20}


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
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    n = int(p["adx_period"])
    atr = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / atr, 100 * _rma(mdm, n) / atr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), n)
    kk = int(p["stoch_k_period"])
    rng = h.rolling(kk).max() - lo.rolling(kk).min()
    k = (100 * (c - lo.rolling(kk).min()) / rng.where(rng > 0)).rolling(int(p["stoch_smooth_k"])).mean()
    d = k.rolling(int(p["stoch_d_period"])).mean()
    strong = adx > float(p["adx_threshold"])
    le = strong & (k > d) & (k.shift(1) <= d.shift(1)) & (k < float(p["oversold"]))
    lx = strong & (k < d) & (k.shift(1) >= d.shift(1)) & (k > float(p["overbought"]))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
