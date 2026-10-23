"""Broker days: SuperTrend 3 x 10 and SuperTrend 2 x 14 both turning up goes long, both down goes short; a long closes when the pair stops agreeing up, a short when it stops agreeing down; reversing.
Port of FMZ strategy #436522 "Multi Timeframe Oscillation Channel Trend Tracking Strategy" (Multi Supertrend with no-repaint HTF option strategy (ramki_simple)).

FMZ source id: 436522

Source
    https://www.fmz.com/strategy/436522 (PineScript v4, FMZ last modified 2023-12-25 14:27:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-167), SuperTrend 3 / 10 and 2 / 14; HTF selection off and HTF input empty (the second SuperTrend runs on the chart); VWAP filter off
    [_, Trend] = supertrend(3, 10);  [_, TrendHtf] = supertrend(2, 14) (HTF == '' -> no security);  Long = Trend == -1 and TrendHtf == -1;  Short = both 1
    Long and not Long[1] -> entry long;  Short and not Short[1] -> entry short;  Long[1] and not Long -> close long;  Short[1] and not Short -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Select HTF Automatically" off and an empty HTF input, the f_Security branch never runs: both
      SuperTrends are the chart's own (ta.supertrend, -1 = up). The VWAP filter is off, so volume is not
      used. The entries come on the first bar of agreement; the closes on the first bar it ends. A close
      acts only on a position the bar's entries leave unchanged (call order). REVERSAL INTENDED. qty 1 is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two-SuperTrend agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 unit, not ported.
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

NAME = "fmz_436522_dual_supertrend_agreement_daily_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult1": [3.0, 2.0],
    "mult2": [2.0, 1.5],
}
DEFAULT_PARAMS = {"mult1": 3.0, "period1": 10, "mult2": 2.0, "period2": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, t1 = _supertrend(bars_df, float(p["mult1"]), int(p["period1"]))
    _, t2 = _supertrend(bars_df, float(p["mult2"]), int(p["period2"]))
    lg = ((t1 == -1) & (t2 == -1)).to_numpy()
    sh = ((t1 == 1) & (t2 == 1)).to_numpy()
    lg1 = np.concatenate(([False], lg[:-1]))
    sh1 = np.concatenate(([False], sh[:-1]))
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if lg[i] and not lg1[i] and pos != 1:
            le[i], pos = True, 1
        elif sh[i] and not sh1[i] and pos != -1:
            se[i], pos = True, -1
        elif pos == 1 and lg1[i] and not lg[i]:
            lx[i], pos = True, 0
        elif pos == -1 and sh1[i] and not sh[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
