"""Alpha RSI breakout, broker days, long only: RSI 14 crossing above 34 while the close is above SMA 200
goes long; the long closes when RSI reaches 50 or falls to 30.
Port of FMZ strategy #428619 "Alpha RSI Breakout Trading Strategy".

FMZ source id: 428619

Source
    https://www.fmz.com/strategy/428619 (PineScript v5, FMZ last modified 2023-10-07 15:45:07).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 201-244), SMA 200, RSI 14, entry 34, stop 30, take-profit 50
    crossover(rsi, 34) and close > sma200 -> entry long
    close when rsi <= 30, or rsi >= 50 (both branches of the activation flag close at 50)
    "trailing stop": trailingStop = the lowest close since entry; close < trailingStop -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN the "trailing stop" can never fire: it is the lowest close so far, updated before
      the check on the same bar, so the close is never below it. Not ported.
    * The strategy() line is commented out: Pine defaults. An entry and a close on one bar: the
      close acts only on an open position. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and MA length.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() settings stored in original_sizing.txt.
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

NAME = "fmz_428619_alpha_rsi_breakout_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_entry": [34, 40],
    "sma_length": [200, 100],
}
DEFAULT_PARAMS = {"sma_length": 200, "rsi_length": 14, "rsi_entry": 34, "rsi_stop_loss": 30, "rsi_take_profit": 50}


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
    sma = c.rolling(int(p["sma_length"])).mean()
    d = c.diff()
    n = int(p["rsi_length"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    enter = ((rsi > p["rsi_entry"]) & (rsi.shift(1) <= p["rsi_entry"]) & (c > sma)).to_numpy()
    exit_ = ((rsi <= p["rsi_stop_loss"]) | (rsi >= p["rsi_take_profit"])).to_numpy()
    m = len(enter)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0 and enter[i]:
            pos = 1
        if start == 1 and exit_[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
