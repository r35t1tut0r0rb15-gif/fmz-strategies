"""RMA envelope breakouts, long only, broker days: the high crossing over the 6-bar RMA of closes plus 1.9 % goes long; the low crossing under the RMA minus 1.5 % closes.
Port of FMZ strategy #439349 "Simple Trailing Stop Buy Strategy Based on Percentage" (Simple Trailing Buy & Stop Strategy).

FMZ source id: 439349

Source
    https://www.fmz.com/strategy/439349 (PineScript v2, FMZ last modified 2024-01-19 14:30:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-164), stop offset 1.5 %; trailing buy offset 1.9 %; 6 bars; sources close / close, triggers low / high
    tsl = rma(close, 6) x (1 - 1.5 %);  tbuy = rma(close, 6) x (1 + 1.9 %);  crossover(high, tbuy) -> entry Long;  crossunder(low, tsl) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and the close act on the position held at the bar close: from flat the entry opens (the
      close has nothing to close); a long meeting both closes. Long only. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent envelope crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439349_rma_envelope_breakout_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "offset": [1.5, 3.0],
    "buyoffset": [1.9, 3.0],
}
DEFAULT_PARAMS = {"offset": 1.5, "buyoffset": 1.9, "sumbars": 6}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    base = _rma(c, int(p["sumbars"]))
    tsl = base * (1 - float(p["offset"]) / 100)
    tbuy = base * (1 + float(p["buyoffset"]) / 100)
    xo = ((h > tbuy) & (h.shift(1) <= tbuy.shift(1))).to_numpy()
    xu = ((lo < tsl) & (lo.shift(1) >= tsl.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xu[i]:
            lx[i], pos = True, 0
        elif pos == 0 and xo[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
