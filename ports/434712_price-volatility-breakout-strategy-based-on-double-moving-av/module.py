"""Decision Point price momentum oscillator colour changes, broker days: the histogram (PMO less its EMA 10) turning bright
green (positive and rising) goes long; turning dark green or red closes the long; turning red (negative and falling) goes
short; turning orange or bright green closes the short.
Port of FMZ strategy #434712 "Price Volatility Breakout Strategy Based on Double Moving Averages" (Strategy for DPMO).

FMZ source id: 434712

Source
    https://www.fmz.com/strategy/434712 (PineScript v2, FMZ last modified 2023-12-08 16:44:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 118-156), smoothing 35 / 20, signal 10
    csf(x, n) = (x - csf[1]) x 2 / n + csf[1] (from 0);  pmo = csf(10 csf(100 close / close[1] - 100, 35), 20);  d = pmo - ema(pmo, 10)
    colour lime (d > 0, rising) / green (d > 0) / red (d <= 0, falling) / orange;  lime starts -> entry long;  green or red starts -> close long;  red starts -> entry short;  orange or lime starts -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The custom smoothing starts from 0 (nz), as written. The closes act on the position held on
      the bar; an entry on the same bar wins. strategy.entry reverses: REVERSAL INTENDED. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a momentum oscillator's colour states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_434712_dpmo_colour_states"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [35, 20],
    "siglen": [10, 5],
}
DEFAULT_PARAMS = {"len1": 35, "len2": 20, "siglen": 10}


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


def _csf(x, n):
    sm = 2.0 / n
    out = np.zeros(len(x))
    prev = 0.0
    for i in range(len(x)):
        prev = (x[i] - prev) * sm + prev
        out[i] = prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    c1 = np.concatenate(([cv[0]], cv[:-1])) if len(cv) else cv
    pm2 = _csf(cv / c1 * 100 - 100, int(p["len1"]))
    pmo = pd.Series(_csf(10 * pm2, int(p["len2"])), index=c.index)
    d = pmo - pmo.ewm(span=int(p["siglen"]), adjust=False).mean()
    dv, d1 = d.to_numpy(), d.shift(1).to_numpy()
    with np.errstate(invalid="ignore"):
        hc = np.where(dv > 0, np.where(dv > d1, 1, 2), np.where(dv < d1, 3, 4))   # 1 lime 2 green 3 red 4 orange
    h1 = np.concatenate(([0], hc[:-1]))
    start = lambda k: (hc == k) & (h1 != k)  # noqa: E731
    buy, cbuy, sell, csell = start(1), start(2), start(3), start(4)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and (cbuy[i] or sell[i]):
            new = 0
        if pos == -1 and (csell[i] or buy[i]):
            new = 0
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
