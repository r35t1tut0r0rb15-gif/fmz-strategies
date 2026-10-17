"""HPotter fractal chaos bands, broker days: the upper band is the last confirmed fractal high (a high with lower highs on
each side), the lower band the last fractal low; a close above the upper band goes long, below the lower band goes short;
held in between and reversed on the opposite break.
Port of FMZ strategy #435123 "Trend Trading Strategy Based on Price Extremum" (Fractal Chaos Bands).

FMZ source id: 435123

Source
    https://www.fmz.com/strategy/435123 (PineScript v2, FMZ last modified 2023-12-12 14:36:14).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 141-175), pattern 1; reverse false
    fractalUp: high[p + 1] with high[i] < high[i + 1] for i = p .. 1 and high[i] < high[i - 1] for i = p + 2 .. 2 p + 1 -> band = that high, else band[1]
    pos = close > upper ? 1 : close < lower ? -1 : pos[1];  1 -> entry long;  -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A fractal is confirmed pattern bars after its bar (only past bars read). strategy.entry
      reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND427136 (2 members, best partner #427136, Jaccard 0.743); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435123_fractal_chaos_bands"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pattern": [1, 2, 3],
}
DEFAULT_PARAMS = {"pattern": 1}


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


def _band(x, pt, high):
    """Last confirmed fractal (pt bars each side) as of each bar; x[t - k] is written x_k."""
    m = len(x)
    out = np.full(m, np.nan)
    last = np.nan
    for t in range(m):
        if t >= 2 * pt + 1:
            xk = lambda k: x[t - k]  # noqa: E731
            if high:
                okl = all(xk(i) < xk(i + 1) for i in range(pt, 0, -1))
                okr = all(xk(i) < xk(i - 1) for i in range(pt + 2, 2 * pt + 2))
            else:
                okl = all(xk(i) > xk(i + 1) for i in range(pt, 0, -1))
                okr = all(xk(i) > xk(i - 1) for i in range(pt + 2, 2 * pt + 2))
            if okl and okr:
                last = xk(pt + 1)
        out[t] = last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pt = int(p["pattern"])
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    cv = bars_df["close"].to_numpy(dtype=float)
    up_b, dn_b = _band(hv, pt, True), _band(lv, pt, False)
    with np.errstate(invalid="ignore"):
        up, dn = cv > up_b, cv < dn_b
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
