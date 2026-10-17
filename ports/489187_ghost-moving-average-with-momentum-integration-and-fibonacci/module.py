"""Ghost (Hull) MA 20 crosses with normalised momentum and a Fibonacci-range bracket, three-day bars: the close crossing
above the Hull MA 20 with positive smoothed momentum goes long, with a target 0.618 and a stop 0.382 of the 50-bar
range away; the mirror goes short.
Port of FMZ strategy #489187 "幽灵移动平均与动量结合的斐波那契目标价与止损策略-Ghost-Moving-Average-with-Momentum-Integration-and-Fibonacci-Target-Stop-Loss-Strategy" (Ghost MA + Momentum + Fib TP/SL + Dashboard).

FMZ source id: 489187

Source
    https://www.fmz.com/strategy/489187 (PineScript v5, FMZ last modified 2025-04-02 15:33:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 144-190), GMA 20, momentum 20 smoothed 10, swing 50
    gma = WMA(2 x WMA(src, 10) - WMA(src, 20), round(sqrt(20)));  mom = src - src[20]
    norm = EMA 10 of mom / stdev(mom, 20)
    long = crossover(src, gma) and norm > 0 -> entry + exit(limit = close + 0.618 range, stop = close - 0.382 range)
    short mirrored;  range = highest(high, 50) - lowest(low, 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: tp_stop = 0.618 x range / close, sl_stop = 0.382 x range / close,
      shifted one bar inside stops(), re-based on the fill (house rule). TP2 / TP3 are only displayed.
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot fall on one bar.
    * FREQ = "3D" from the backtest header (period 3d): three-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509: coarse_bar_stop. Stop module: portfolio_kwargs {} (D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, moving averages, normalised momentum and range fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489187_ghost_ma_momentum_fib_bracket"
FAMILY = "hull_ma"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "gma_len": [20, 40],
    "swing": [50, 100],
}
DEFAULT_PARAMS = {"gma_len": 20, "mom_len": 20, "mom_smooth": 10, "swing": 50, "tp_fib": 0.618, "sl_fib": 0.382}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["gma_len"])
    gma = _wma(2 * _wma(c, max(n // 2, 1)) - _wma(c, n), max(int(round(np.sqrt(n))), 1))
    k = int(p["mom_len"])
    mom = c - c.shift(k)
    norm = mom.ewm(span=int(p["mom_smooth"]), adjust=False).mean() / mom.rolling(k).std(ddof=0)
    long_e = ((c > gma) & (c.shift(1) <= gma.shift(1)) & (norm > 0)).astype(bool)
    short_e = ((c < gma) & (c.shift(1) >= gma.shift(1)) & (norm < 0)).astype(bool)
    s = int(p["swing"])
    rng = (h.rolling(s).max() - lo.rolling(s).min()) / c
    return long_e, short_e, rng


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, rng = _setup(bars_df, p)
    return {"sl_stop": (p["sl_fib"] * rng).shift(1), "tp_stop": (p["tp_fib"] * rng).shift(1)}


def portfolio_kwargs(**params):
    return {}
