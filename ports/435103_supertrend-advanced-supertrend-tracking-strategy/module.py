"""Close-based ATR stop-and-reverse line, broker days: the line is the close less 1.5 ATR 14 while the close stays above the
previous line, and the close plus 1.5 ATR once it falls below; the close crossing above the line goes long, crossing below
goes short (reversing).
Port of FMZ strategy #435103 "基于SuperTrend的趋势跟踪策略Advanced-SuperTrend-Tracking-Strategy" (Advanced Trend Strategy).

FMZ source id: 435103

Source
    https://www.fmz.com/strategy/435103 (PineScript v5, FMZ last modified 2023-12-12 12:27:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-160), ATR 14 x 1.5 on close
    st = na(st) ? close - 1.5 atr : st;  close > st -> st = close - 1.5 atr;  close < st -> st = close + 1.5 atr
    crossover(close, st) -> entry long (close short);  crossunder(close, st) -> entry short (close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is rebuilt from the current close each bar, as written (it does not ratchet). The
      crosses compare the close with the line after this bar's update. strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435103_close_atr_line_flips"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 3.0],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"mult": 1.5, "atr_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    k = float(p["mult"])
    m = len(cv)
    st = np.full(m, np.nan)
    s = np.nan
    for i in range(m):
        up, dn = cv[i] - k * atr[i], cv[i] + k * atr[i]
        if np.isnan(s):
            s = up
        if cv[i] > s:
            s = up
        if cv[i] < s:
            s = dn
        st[i] = s
    s1 = np.concatenate(([np.nan], st[:-1]))
    c1v = np.concatenate(([np.nan], cv[:-1]))
    with np.errstate(invalid="ignore"):
        le = (cv > st) & (c1v <= s1)
        se = (cv < st) & (c1v >= s1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
