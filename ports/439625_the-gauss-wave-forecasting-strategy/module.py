"""Open versus a triple-smoothed Gaussian forecast, broker days: an open above the previous bar's forecast (3 g1 - 3 g2 + g3 of four-pole Gaussian filters, period 20) holds a long, below it a short; reversing.
Port of FMZ strategy #439625 "The Gauss Wave Forecasting Strategy" (Gaussbot v1.0).

FMZ source id: 439625

Source
    https://www.fmz.com/strategy/439625 (PineScript v2, FMZ last modified 2024-01-22 12:37:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-193), length 20; source open
    ret = four-pole Gaussian filter of open (nz history);  ret2 = the same filter of ret;  ret3 of ret2;  ret4 = 3 ret - 3 ret2 + ret3
    long = open - ret4[1] > 0;  short = open - ret4[1] < 0;  the if-blocks assign new local variables (no effect);  long and not short -> entry long;  short and not long -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filters start from zero history (nz), as written. In version 2 an assignment inside an if
      block declares a new local variable, so the two "hold the previous value" blocks change nothing.
      The source is the bar's open, known at its start. A same-side entry while in the position is
      ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Gaussian filter forecast.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439625_gauss_wave_forecast_open_side"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p": [20, 40, 10],
}
DEFAULT_PARAMS = {"p": 20}


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


def _gauss(x, a):
    """The script's four-pole filter with nz history."""
    m = len(x)
    out = np.zeros(m)
    b = 1 - a
    for i in range(m):
        r = [out[i - k] if i - k >= 0 else 0.0 for k in (1, 2, 3, 4)]
        out[i] = (a ** 4 * x[i] + 4 * b * r[0] - 6 * b ** 2 * r[1] + 4 * b ** 3 * r[2] - b ** 4 * r[3])
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ov = bars_df["open"].to_numpy(dtype=float)
    w = 2 * 3.1415926535 / int(p["p"])
    beta = (1 - np.cos(w)) / (1.414 ** (2.0 / 3) - 1)
    alfa = -beta + np.sqrt(beta * beta + 2 * beta)
    g1 = _gauss(ov, alfa)
    g2 = _gauss(g1, alfa)
    g3 = _gauss(g2, alfa)
    g4 = pd.Series(3 * g1 - 3 * g2 + g3, index=bars_df.index)
    o = bars_df["open"]
    d = o - g4.shift(1)
    lc, sc = d > 0, d < 0
    false = pd.Series(False, index=o.index)
    return lc & ~sc, false, sc & ~lc, false.copy()


def portfolio_kwargs(**params):
    return {}
