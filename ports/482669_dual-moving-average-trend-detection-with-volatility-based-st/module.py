"""EMA 9 / 21 crosses, reversing, with a 1.5 ATR stop from the entry, daily bars.
Port of FMZ strategy #482669 "双均线趋势判断与波动率止损策略-Dual-Moving-Average-Trend-Detection-with-Volatility-Based-Stop-Loss-Strategy" (EMA 9/21 + ATR SL Strategy).

FMZ source id: 482669

Source
    https://www.fmz.com/strategy/482669 (PineScript v5, FMZ last modified 2025-02-27 17:57:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 86-122), EMA 9 / 21, ATR 14 x 1.5
    crossover -> entry long; crossunder -> entry short
    while long, every bar: exit(stop = position_avg_price - 1.5 ATR) (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is measured from strategy.position_avg_price but re-issued every bar with the CURRENT ATR (a moving
      level): fixed at entry as 1.5 ATR / close of the signal bar, shifted one bar inside stops() and re-based on the
      fill; mark trailing_stop_pending. Applied from the fill (decision owed as #489289).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (marked).
    2 generic: PASS, two EMAs and an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the stop via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482669_ema9_21_cross_atr_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "atr_len": 14, "atr_mult": 1.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)}


def portfolio_kwargs(**params):
    return {}
