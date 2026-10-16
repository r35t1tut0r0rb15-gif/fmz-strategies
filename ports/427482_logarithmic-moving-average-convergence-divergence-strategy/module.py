"""Logarithmic MACD, broker days: log(EMA 12) - log(EMA 26) against its EMA 9; the histogram crossing
above 0 goes long, below 0 goes short (always in the market after the first cross).
Port of FMZ strategy #427482 "Logarithmic Moving Average Convergence Divergence Strategy".

FMZ source id: 427482

Source
    https://www.fmz.com/strategy/427482 (PineScript v3, FMZ last modified 2023-09-21 15:38:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 172-204), 12 / 26 / 9, EMAs (SMA switches off)
    lmacd = log(fast_ma) - log(slow_ma); hist = lmacd - ema(lmacd, 9)
    crossover(hist, 0) -> entry long; crossunder(hist, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMA switches are off by default; the grid tries the oscillator SMA switch.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a log ratio of averages (scale-free).
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

NAME = "fmz_427482_log_macd"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50],
    "sma_source": [False, True],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "sma_source": False, "sma_signal": False}


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
    c = bars_df["close"]

    def ma(x, n, simple):
        return x.rolling(n).mean() if simple else x.ewm(span=n, adjust=False).mean()

    f = ma(c, int(p["fast"]), bool(p["sma_source"]))
    s = ma(c, int(p["slow"]), bool(p["sma_source"]))
    lm = np.log(f) - np.log(s)
    hist = lm - ma(lm, int(p["signal"]), bool(p["sma_signal"]))
    up = ((hist > 0) & (hist.shift(1) <= 0)).to_numpy()
    dn = ((hist < 0) & (hist.shift(1) >= 0)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
