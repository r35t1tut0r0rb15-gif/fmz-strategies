"""Smoothed RSI direction with CCI sign in a moving market, broker days: the EMA 12 of an RSI 19 rising with the CCI 13
positive and the 30-bar rate of change (EMA 15) beyond +-3.5 % turns the state long, the mirror short; each turn enters
that side with a 3 % stop from the fill.
Port of FMZ strategy #432908 "基于Stochastic指标和CCI指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Stochastic-and-CCI" (Stochastic CCI BF).

FMZ source id: 432908

Source
    https://www.fmz.com/strategy/432908 (PineScript v4, FMZ last modified 2023-11-22 16:23:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-219), CCI 13, RSI 19 / EMA 12, ROC 30 / EMA 15 with 7 % (half each side), stop 3 %
    long = ema(rsi19, 12) rising and |ema(roc30, 15)| > 3.5 and cci13 > 0;  short mirror
    long_signal = the latest long newer than the latest short (turning on) -> entry long, exit(stop = avg x 0.97 from the next bar)
    short_signal mirror -> entry short, exit(stop = avg x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * last_long / last_short hold the bar time of the latest long / short condition; their crossover
      is the bar where the latest condition changes side, ported as a state turning. The stop is a
      fixed fraction of the fill by side; Pine places it from the bar after the signal, the house
      stop is live on the fill bar too (stated), as #432181.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; stops on daily bars: mark coarse_bar_stop.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, RSI direction, CCI sign, rate of change and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_432908_rsi_ema_cci_roc_turn"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pcnt": [7.0, 3.0],
    "sl_pct": [3.0, 6.0],
}
DEFAULT_PARAMS = {"cci_len": 13, "rsi_len": 19, "rsi_ema": 12, "roc_len": 30, "pcnt": 7.0, "sl_pct": 3.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: float(np.mean(np.abs(a - a.mean()))), raw=True)
    cci = (c - ma) / (0.015 * dev)
    d = c.diff()
    rl = int(p["rsi_len"])
    up = d.clip(lower=0).ewm(alpha=1 / rl, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / rl, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(~((up == 0) & (dn != 0)), 0.0)
    out = rsi.ewm(span=int(p["rsi_ema"]), adjust=False).mean()
    k = int(p["roc_len"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    eroc = roc.ewm(span=k // 2, adjust=False).mean()
    h = float(p["pcnt"]) / 2
    moving = (eroc > h) | (eroc < -h)
    lg = ((out > out.shift(1)) & moving & (cci > 0)).to_numpy()
    sh = ((out < out.shift(1)) & moving & (cci < 0)).to_numpy()
    m = len(c)
    st = np.zeros(m, dtype=np.int8)
    s = 0
    for i in range(m):
        if lg[i]:
            s = 1
        elif sh[i]:
            s = -1
        st[i] = s
    prev = np.concatenate(([0], st[:-1]))
    le = (st == 1) & (prev != 1)
    se = (st == -1) & (prev != -1)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = np.zeros(len(le), dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    sl = pd.Series(np.where(le | se, float(p["sl_pct"]) / 100, np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
