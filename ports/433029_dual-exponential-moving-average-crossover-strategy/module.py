"""DEMA 8 / 20 / 63 state, broker days: with the DEMA 8 of ohlc4 above both the DEMA 20 of the lows and the DEMA 63 of the
closes the strategy is long, below both short; otherwise it keeps its position.
Port of FMZ strategy #433029 "Dual Exponential Moving Average Crossover Strategy" (Double Exponential Moving Average 8-20-63 Strategy).

FMZ source id: 433029

Source
    https://www.fmz.com/strategy/433029 (PineScript v4, FMZ last modified 2023-11-23 17:34:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-188), DEMA 8 (ohlc4), DEMA 20 (low), DEMA 63 (close)
    dema(x, n) = 2 ema(x, n) - ema(ema(x, n), n)
    longC = dema1 > dema2 and dema1 > dema3 -> entry long;  shortC = dema1 < dema2 and dema1 < dema3 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are levels: a repeated entry in the same direction is ignored (pyramiding 0), so the
      state flips only when the other condition holds. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
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

NAME = "fmz_433029_dema_8_20_63_state"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short": [8, 5],
    "long2": [63, 100],
}
DEFAULT_PARAMS = {"short": 8, "long": 20, "long2": 63}


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


def _dema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    return 2 * e1 - e1.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    d1 = _dema((o + h + lo + c) / 4, int(p["short"]))
    d2 = _dema(lo, int(p["long"]))
    d3 = _dema(c, int(p["long2"]))
    lc = ((d1 > d2) & (d1 > d3)).to_numpy()
    sc = ((d1 < d2) & (d1 < d3)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(x, index=bars_df.index)
                 for x in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
