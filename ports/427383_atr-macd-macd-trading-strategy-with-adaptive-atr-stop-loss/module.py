"""MACD BF on broker days: the MACD (EMA 13 - EMA 30) crossing above its EMA 12 goes long, crossing
below goes short (each reverses the other side); each new side has a stop 1.25 x ATR(2) beyond the
signal bar's close.
Port of FMZ strategy #427383 "MACD Trading Strategy with Adaptive ATR Stop Loss".

FMZ source id: 427383

Source
    https://www.fmz.com/strategy/427383 (PineScript v4, FMZ last modified 2023-09-20 15:23:00).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 166-238), MACD 13 / 30 / 12, ATR stop 2 x 1.25
    delta = (ema13 - ema30) - ema(ema13 - ema30, 12)
    crossover(delta, 0) -> entry long; crossunder(delta, 0) -> entry short
    longStop = close[signal bar] - 1.25 atr(2)[signal bar], placed from the bar after the signal (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed at the signal bar: sl_stop = 1.25 x ATR(2) / close of the signal bar, shifted
      one bar inside stops() (known at the fill bar's open), re-based on the fill price. The crosses
      alternate, so each entry has its own signal-bar stop (no re-entry case as in #427304).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; stops on
      daily bars: mark coarse_bar_stop.
    * testPeriod() is the constant true. Stop module: portfolio_kwargs {} (driver D4);
      REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is fixed at the signal.
    2 generic: PASS, MACD crosses and an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; the stop ported via stops().
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427304 (3 members, with #427304, Jaccard 0.676); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427383_macd_bf_atr_stop"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [13, 8],
    "slow": [30, 50],
    "atr_mult": [1.25, 2.5],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 30, "signal": 12, "atr_period": 2, "atr_mult": 1.25}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up = ((delta > 0) & (delta.shift(1) <= 0)).astype(bool)
    dn = ((delta < 0) & (delta.shift(1) >= 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false.copy(), dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = p["atr_mult"] * _atr(bars_df, int(p["atr_period"])) / bars_df["close"]
    return {"sl_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
