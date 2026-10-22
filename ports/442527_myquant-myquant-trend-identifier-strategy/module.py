"""Colour states of the slope and curvature of a normalised ALMA(140), daily bars, long only: from flat, a turn to green (slope and curvature both up) after red, blue or yellow under set slope-average
limits, with a 120-bar heat index under 85, goes long; a turn to red, or green to yellow, under the mirror limits closes.
Port of FMZ strategy #442527 "MyQuant趋势识别策略MyQuant-Trend-Identifier-Strategy" (Trend Identifier Strategy).

FMZ source id: 442527

Source
    https://www.fmz.com/strategy/442527 (PineScript v5, FMZ last modified 2024-02-22 16:04:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-174), ALMA 140 / 1.1 / 6; daily tfc 24 (EMA 120, stoch 120, EMA 7); pyramiding 10; 100 % of equity, capital 1000, commission 0.03; time window off
    dema = (alma - alma[1]) / alma;  d2ema = ema(dema - dema[1], 5);  colour: green dema > 0, d2 > 0; yellow dema > 0, d2 < 0; red both < 0; blue dema < 0, d2 > 0;  demaema = ema(dema, 21)
    ind = (close - ema(close, 120)) / close;  index = ema(ema(stoch(ind, 120), 3), 7)
    flat: ((red / blue with demaema < 0.02, or yellow with demaema > -0.02) then green, or red then blue with demaema < -0.01) and index < 85 and ind < 0.4 -> entry buy (equity / close)
    long: ((yellow > -0.02, blue < 0.02 or green < 0.02) then red, or green then yellow with demaema > 0.015) and index > 15 and ind > -0.1 -> order sell position_size

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars tfc = 24, so the lengths are 120 / 120 / 7, as written. The entry needs no open
      long (position_size <= 0) and the sell order is the whole long, so one long is open at a time
      despite pyramiding 10. The ALMA offset 1.1 is as written. The two stochastic lines only plot.
      The quantity (equity / close) is sizing. Long only. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ALMA slope / curvature colour states with a heat filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity quantity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442527_alma_slope_colour_heat_filter_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "alma_len": [140, 70],
    "heat_len": [120, 60],
}
DEFAULT_PARAMS = {"alma_len": 140, "heat_len": 120, "alma_offset": 1.1, "alma_sigma": 6.0, "index_len": 7}

GREEN, YELLOW, RED, BLUE = 1, 2, 3, 4


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


def _alma(x, n, off, sig):
    mm = off * (n - 1)
    s = n / sig
    w = np.exp(-((np.arange(n) - mm) ** 2) / (2 * s * s))
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _stoch(x, n):
    lo, hi = x.rolling(n).min(), x.rolling(n).max()
    return 100.0 * (x - lo) / (hi - lo).where(hi > lo)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = _alma(c, int(p["alma_len"]), float(p["alma_offset"]), float(p["alma_sigma"]))
    dema = (a - a.shift(1)) / a
    d2 = _ema(dema - dema.shift(1), 5)
    tc = np.select([(dema > 0) & (d2 > 0), (dema > 0) & (d2 < 0), (dema < 0) & (d2 < 0), (dema < 0) & (d2 > 0)],
                   [GREEN, YELLOW, RED, BLUE], 0)
    tc1 = np.concatenate(([0], tc[:-1]))
    de = _ema(dema, 21).to_numpy()
    hl = int(p["heat_len"])
    ind = (c - _ema(c, hl)) / c
    index = _ema(_ema(_stoch(ind, hl), 3), int(p["index_len"])).to_numpy()
    iv = ind.to_numpy()
    with np.errstate(invalid="ignore"):
        buy = ((((tc1 == RED) & (de < 0.02)) | ((tc1 == BLUE) & (de < 0.02)) | ((tc1 == YELLOW) & (de > -0.02)))
               & (tc == GREEN)) | ((tc1 == RED) & (tc == BLUE) & (de < -0.01))
        buy = buy & (index < 85) & (iv < 0.4)
        sell = ((((tc1 == YELLOW) & (de > -0.02)) | ((tc1 == BLUE) & (de < 0.02)) | ((tc1 == GREEN) & (de < 0.02)))
                & (tc == RED)) | ((tc1 == GREEN) & (tc == YELLOW) & (de > 0.015))
        sell = sell & (index > 15) & (iv > -0.1)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if not held and buy[i]:
            le[i] = True
        elif held and sell[i]:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
