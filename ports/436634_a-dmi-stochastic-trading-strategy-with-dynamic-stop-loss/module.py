"""Directional movement with a stochastic extreme, broker days: DI+ over DI- with ADX over 25 and the stochastic %K under 20 goes long; DI- over DI+ with ADX over 25 and %K over 80 goes short (reversing); each entry carries a stop at
the lowest (long) or highest (short) close of the history so far.
Port of FMZ strategy #436634 "A DMI Stochastic Trading Strategy with Dynamic Stop loss" (DMI with Stochastic and Dynamic Stop-Loss).

FMZ source id: 436634

Source
    https://www.fmz.com/strategy/436634 (PineScript v5, FMZ last modified 2023-12-26 14:30:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 170-195), DMI 14 / 14, ADX threshold 25, stochastic %K 14
    longCondition = diPlus > diMinus and adx > 25 and stochK < 20;  shortCondition = diMinus > diPlus and adx > 25 and stochK > 80
    lowestClose = running minimum of close, highestClose = running maximum;  entry Buy + exit("Exit Buy", stop = lowestClose);  entry Sell + exit("Exit Sell", stop = highestClose)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop is the running extreme close of the loaded history, so it is a price level; it is
      re-expressed as a distance, sl_stop = (signal close - running extreme close) / signal close (the
      long) or (running maximum - close) / close (the short), shifted one bar inside stops() (re-based
      on the fill); an extreme made by the signal bar itself would be a zero distance and is floored at
      1e-6, which exits at once as the level equals the close. The running extreme depends on where the
      loaded data starts. The %D length is unused. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute; stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop level fixed at entry.
    2 generic: ADAPT, stop level -> distance fraction.
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

NAME = "fmz_436634_dmi_stoch_extreme_close_stop"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 10],
    "adx_threshold": [25, 20],
}
DEFAULT_PARAMS = {"length": 14, "adx_threshold": 25, "stoch_k": 14, "stoch_lo": 20, "stoch_hi": 80}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    up, down = h.diff(), -lo.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    di_plus, di_minus = 100 * _rma(plus_dm, n) / atr, 100 * _rma(minus_dm, n) / atr
    with np.errstate(divide="ignore", invalid="ignore"):
        dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus)
    adx = _rma(dx, n)
    k = int(p["stoch_k"])
    ll, hh = lo.rolling(k).min(), h.rolling(k).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        stoch = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    thr = float(p["adx_threshold"])
    long_c = ((di_plus > di_minus) & (adx > thr) & (stoch < float(p["stoch_lo"]))).fillna(False)
    short_c = ((di_minus > di_plus) & (adx > thr) & (stoch > float(p["stoch_hi"]))).fillna(False)
    return long_c.astype(bool), short_c.astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    long_c, _ = _signals(bars_df, p)
    l_f = (c - c.cummin()) / c                         # long: distance to the lowest close so far
    s_f = (c.cummax() - c) / c                         # short: distance to the highest close so far
    sl = l_f.where(long_c, s_f).clip(lower=1e-6)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
