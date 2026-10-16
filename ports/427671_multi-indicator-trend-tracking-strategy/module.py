"""Moving-average speed vote, broker days: three votes (the MACD signal line rising or falling, the
stochastic K oversold or overbought, the 10-bar average rate of change of SMA 50 above or below 0);
two long votes go long, two short votes go short.
Port of FMZ strategy #427671 "Multi-Indicator Trend Tracking Strategy" ("Mov Avg Speed Strategy").

FMZ source id: 427671

Source
    https://www.fmz.com/strategy/427671 (PineScript v5, FMZ last modified 2023-09-23 15:19:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 242-307), SMA 50, ROC 1, avg ROC 10, stoch 14/3 (80/20), MACD 12/26/9
    avg_roc = sma(roc(sma(close, 50), 1), 10): > 0 long vote, < 0 short vote
    k = sma(stoch(close, high, low, 14), 3): <= 20 long vote, >= 80 short vote
    macd_avg = ema(ema12 - ema26, 9): rising long vote, falling short vote
    long_count >= 2 -> entry long; short_count >= 2 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source input is close (default). strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, indicator lengths and levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427671_ma_speed_three_vote"
FAMILY = "multi_indicator_vote"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "avg_len": [50, 20],
    "avg_roc_len": [10, 5],
    "stoch_len": [14, 7],
}
DEFAULT_PARAMS = {"avg_len": 50, "roc_len": 1, "avg_roc_len": 10, "stoch_len": 14, "smooth_k": 3,
                  "overbought": 80, "oversold": 20, "fast": 12, "slow": 26, "macd_avg": 9}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    avg = c.rolling(int(p["avg_len"])).mean()
    rl = int(p["roc_len"])
    roc = 100 * (avg - avg.shift(rl)) / avg.shift(rl)
    avg_roc = roc.rolling(int(p["avg_roc_len"])).mean()
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    ma = macd.ewm(span=int(p["macd_avg"]), adjust=False).mean()
    long_n = (ma > ma.shift(1)).astype(int) + (k <= p["oversold"]).astype(int) + (avg_roc > 0).astype(int)
    short_n = (ma < ma.shift(1)).astype(int) + (k >= p["overbought"]).astype(int) + (avg_roc < 0).astype(int)
    le, se = (long_n >= 2).to_numpy(), (short_n >= 2).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
