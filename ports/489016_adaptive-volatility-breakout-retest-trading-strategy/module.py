"""SMA 200 crosses with a retest and a tight ATR bracket, broker days: the close crossing above SMA 200 with a low at or
below it within the last five bars goes long; the mirror goes short; each trade has a stop and a target 1 ATR away.
Port of FMZ strategy #489016 "自适应波动突破回撤交易策略-Adaptive-Volatility-Breakout-Retest-Trading-Strategy" (HFT Swing Bot).

FMZ source id: 489016

Source
    https://www.fmz.com/strategy/489016 (PineScript v5, FMZ last modified 2025-04-01 10:54:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-196), SMA 200, ATR 14 x 1
    long = crossover(close, sma200) and lowest(low, 5) <= sma200;  short = crossunder and highest(high, 5) >= sma200
    -> entry + exit(stop = close -+ 1 ATR, limit = close +- 1 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 5-bar windows include the current bar. The bracket is placed once, on the signal bar: sl_stop = tp_stop =
      ATR / close, shifted one bar inside stops(), re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED); the two crosses cannot fall on one bar. The title's "HFT" is a label.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, an SMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489016_sma200_cross_retest_atr_bracket"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_factor": [1.0, 2.0],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"ma_len": 200, "risk_factor": 1.0, "atr_len": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["ma_len"])).mean()
    up = (c > ma) & (c.shift(1) <= ma.shift(1))
    dn = (c < ma) & (c.shift(1) >= ma.shift(1))
    long_e = (up & (lo.rolling(5).min() <= ma)).astype(bool)
    short_e = (dn & (h.rolling(5).max() >= ma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = (p["risk_factor"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": d, "tp_stop": d}


def portfolio_kwargs(**params):
    return {}
