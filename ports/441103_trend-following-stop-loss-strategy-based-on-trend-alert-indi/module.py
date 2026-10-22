"""Always-long re-entry with a structure stop, broker days, long only: from flat the long opens (the TrendAlert source is the close, always positive) with a stop 0.2 ATR(15) under the 8-bar low and a
target half the stop distance above the signal close; after an exit it re-opens on the next bar.
Port of FMZ strategy #441103 "Trend Following Stop Loss Strategy Based on Trend Alert Indicator" (TrendAlert Based).

FMZ source id: 441103

Source
    https://www.fmz.com/strategy/441103 (PineScript v5, FMZ last modified 2024-02-05 16:00:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-265), TrendAlert source close; ATR 15; structure on, lookback 8; stop x 0.2 ATR; limit x 0.5; alert inputs
    longStop = lowest(low, 8) - 0.2 atr(15);  long = TrendAlert > 0 and flat -> entry long, exit(stop = longStop, limit = (close - longStop) 0.5 + close)
    short = TrendAlert < 0 and flat -> entry short (never: the close is positive)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The TrendAlert input defaults to the close, which is always above 0, so every flat bar opens a long
      and the short side never trades: ported long only. The bracket is placed on the signal bar from its
      values: sl = (close - longStop) / close, tp = 0.5 sl, shifted one bar inside stops() and re-based on
      the fill. The alerts and plots are display only. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, structure stop and half-distance target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the alert risk input stored (not an order size).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441103_always_long_structure_stop_bracket"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [8, 20],
    "limit_mult": [0.5, 1.0],
}
DEFAULT_PARAMS = {"lookback": 8, "limit_mult": 0.5, "atr_len": 15, "atr_mult": 0.2}


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


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    stop = lo.rolling(int(p["lookback"])).min() - _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    sl = (c - stop) / c
    return sl, float(p["limit_mult"]) * sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
