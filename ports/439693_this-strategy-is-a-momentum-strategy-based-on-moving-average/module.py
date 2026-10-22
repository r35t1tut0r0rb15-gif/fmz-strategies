"""SMA 13 / 34 crossings with a 10 % / 30 % bracket, long only, broker days: the SMA 13 crossing over the SMA 34 goes long; the SMA 12 crossing under the SMA 21 closes; each trade has a 10 % stop and a 30 %
target.
Port of FMZ strategy #439693 "This strategy is a momentum strategy based on moving average lines" ({STRATEGY NAME}).

FMZ source id: 439693

Source
    https://www.fmz.com/strategy/439693 (PineScript v3, FMZ last modified 2024-01-23 10:38:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-172), long SMA 13 / 34, short-side SMA 12 / 21; shorts off; stop 10 %, target 30 %; window() true
    buy = crossover(sma 13, sma 34) -> entry Long;  sell = crossunder(sma 12, sma 21) -> (shorts off) close Long;  exit(stop = avg x 0.90, limit = avg x 1.30)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed 10 % / 30 % of the average (fill) price, re-sent every bar at the same
      levels: the port starts it at the fill. The entry and the close act on the position held at the
      bar close: from flat the entry opens (the close has nothing to close); a long meeting both closes.
      The state loop follows the bracket so that later signals see the position it leaves. Long only.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing
      code. Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
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

NAME = "fmz_439693_sma13_34_cross_percent_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.10, 0.05],
    "tp": [0.30, 0.15],
}
DEFAULT_PARAMS = {"sl": 0.10, "tp": 0.30}


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
    c = bars_df["close"]

    def sma(n):
        return c.rolling(n).mean()

    a, b, x, y = sma(13), sma(34), sma(12), sma(21)
    buy = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    sell = ((x < y) & (x.shift(1) >= y.shift(1))).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            px = ov[entry_i]
            if lv[i] <= px * (1 - sl) or hv[i] >= px * (1 + tp):
                pos = 0                                  # flat at this bar's close
        if pos == 1:
            if sell[i]:
                lx[i], pos = True, 0
        elif buy[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
