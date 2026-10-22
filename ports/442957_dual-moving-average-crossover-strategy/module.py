"""EMA 8 crossings of the SMA 200 or SMA 50 in the last four bars with the EMA 21 / SMA 50 order, daily bars: up-crossings with the EMA 21 above the SMA 50 go long, the mirror short; an 8 % stop from the
fill; the target, re-set each bar from that bar's open, is kept pending; reversing.
Port of FMZ strategy #442957 "Dual Moving Average Crossover Strategy" (Cross MA-EMA (Crossover moving averages)).

FMZ source id: 442957

Source
    https://www.fmz.com/strategy/442957 (PineScript v4, FMZ last modified 2024-02-27 16:21:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-241), EMA 8 / 21, SMA 50 / 200; profit / loss 8 %
    long = ema21 > sma50 and (crossover(ema8, sma200) or crossover(ema8, sma50) in this or the last 3 bars) -> entry Enter L;  short mirrored -> entry Enter S
    long held: exit(limit = avg + open x 8 %, stop = avg x (1 - 8 %));  short held: exit(limit = avg - open x 8 %, stop = avg x (1 + 8 %)) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent every bar from the average (fill) price; on the flat signal bar it is na, so it
      is ported active from the fill bar (#440797) as a fixed fraction 0.08 of the fill. The target
      adds 8 % of each bar's own open, a level that moves after entry: kept pending (mark
      trailing_stop_pending). The entries stay true for four bars after a crossing and are refused
      while held. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed from the fill; the moving target pending.
    2 generic: PASS, recent EMA / SMA crossings with an order filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442957_ema8_recent_cross_sma_filter_pct_stop"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "profit": [0.08, 0.04],
    "len3": [50, 100],
}
DEFAULT_PARAMS = {"profit": 0.08, "len3": 50, "len1": 8, "len2": 21, "len4": 200}


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


def _recent(flag, k=4):
    out = flag.copy()
    for j in range(1, k):
        out |= flag.shift(j, fill_value=False)
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    o1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    o2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    o3 = c.rolling(int(p["len3"])).mean()
    o4 = c.rolling(int(p["len4"])).mean()

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    lsig = ((o2 > o3) & (_recent(xo(o1, o4)) | _recent(xo(o1, o3)))).to_numpy()
    ssig = ((o2 < o3) & (_recent(xu(o1, o4)) | _recent(xu(o1, o3)))).to_numpy()
    s_ = float(p["profit"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m:
            if ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
            elif lsig[i] and not ssig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["profit"])}


def portfolio_kwargs(**params):
    return {}
