"""Close crossings of a triple-EMA "Lorenzian" line after a move to its other side, daily bars: the close crossing over the line with the 3-bar low under the line of 3 bars ago goes long, the mirror goes short; a high reaching 1.5 % over the signal close (or a low 1.5 % under it) closes the long at the next open, the mirror closes the short; reversing.
Port of FMZ strategy #458250 "Lorenzian Classification Multi Timeframe Target Strategy" (Lorenzian Classification Strategy with Target and Multi-Timeframe).

FMZ source id: 458250

Source
    https://www.fmz.com/strategy/458250 (PineScript v5, FMZ last modified 2024-07-31 11:49:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-304), EMA 5 of hlc3, EMA of EMA, triple EMA; ci = d / (0.015 x ema(|d|, 5)) x 100; lookback 3; target 1.5 %; higher time frame "D" (the chart itself, plotted only)
    crossover(close, lorenzian) and lowest(low, 3) < lorenzian[3] -> entry Buy, entry = close, target = close x 1.015
    crossunder(close, lorenzian) and highest(high, 3) > lorenzian[3] -> entry Sell, entry = close, target = close x 0.985
    target set: long and high >= target -> close Buy, target = na;  else long and low < entry x 0.985 -> close Buy;  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request on a daily chart is the chart itself and only feeds a plotted line. The exits are
      bar-close tests of the high / low against the signal close's levels, filled at the next open. The
      entries are called before the tests; a close acts only on a position held into the bar and not
      being reversed (#437773), but the levels are cleared as written, so a reversal can leave the new
      trade without levels until the next signal. Repeated signals while held re-set the levels from
      the new close, as written. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target and stop are bar-close tests.
    2 generic: PASS, smoothed-line crossings with a percent target and stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458250_lorenzian_line_cross_pct_target_stop_tests_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
    "lookback": [3, 5],
    "target_pct": [0.015, 0.03],
}
DEFAULT_PARAMS = {"length": 5, "lookback": 3, "target_pct": 0.015}


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
    n, k = int(p["length"]), int(p["lookback"])
    e1 = ((h + lo + c) / 3).ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    d = e1 - e2
    ci = d / (0.015 * d.abs().ewm(span=n, adjust=False).mean()) * 100
    lor = e3 + ci
    buy = ((c > lor) & (c.shift(1) <= lor.shift(1)) & (lo.rolling(k).min() < lor.shift(k))).to_numpy()
    sell = ((c < lor) & (c.shift(1) >= lor.shift(1)) & (h.rolling(k).max() > lor.shift(k))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp = float(p["target_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, target, entry = 0, np.nan, np.nan
    for i in range(m):
        cur = pos
        if buy[i]:
            cur, entry, target = 1, cv[i], cv[i] * (1 + tp)
        if sell[i]:
            cur, entry, target = -1, cv[i], cv[i] * (1 - tp)
        if not np.isnan(target):
            if pos > 0 and (hv[i] >= target or lv[i] < entry * (1 - tp)):
                if cur == 1:
                    cur = 0                      # the close acts only on a long held, not reversed
                target = entry = np.nan
            if pos < 0 and (lv[i] <= target or hv[i] > entry * (1 + tp)):
                if cur == -1:
                    cur = 0
                target = entry = np.nan
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
