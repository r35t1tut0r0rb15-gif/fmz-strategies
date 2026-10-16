"""Alpha short SMA + RSI, 2-day bars, short only: RSI 14 crossing above 51 below SMA 200 goes short; the
short closes on the first close that is not a new low since entry, or when RSI reaches 54 or 32.
Port of FMZ strategy #428681 "SMA and RSI Combination Trading Strategy" (Alpha Short SMA and RSI).

FMZ source id: 428681

Source
    https://www.fmz.com/strategy/428681 (PineScript v5, FMZ last modified 2023-10-08 11:40:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 155-191), SMA 200, RSI 14, entry 51, stop 54, take-profit 32
    crossover(rsi, 51) and close < sma200 -> entry short (trailing level reset)
    while short: if close is a new low since entry, trailingStop = close
    close > trailingStop -> close; rsi >= 54 -> close; rsi <= 32 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN the "trailing stop" is the lowest close since entry, so the short closes on the
      first close that is not a new low (close-checked, at the next open).
    * The strategy() line is commented out: Pine defaults. An entry while short is ignored; a close
      on the entry bar acts only on an open position. Short only (no long entry exists):
      Opposite entries cannot occur.
    * 2-day bars are blocks of broker days counted from 1970-01-01 (as worker A's 2-day ports),
      stamped with the session start. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and MA length.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() settings stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428681 (2 members, best partner #428682, Jaccard 0.901); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Short only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428681_alpha_short_sma_rsi"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_entry": [51, 60],
    "sma_length": [200, 100],
}
DEFAULT_PARAMS = {"sma_length": 200, "rsi_length": 14, "rsi_entry": 51, "rsi_stop": 54, "rsi_take_profit": 32}


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


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_length"])).mean()
    d = c.diff()
    n = int(p["rsi_length"])
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    enter = ((rsi > p["rsi_entry"]) & (rsi.shift(1) <= p["rsi_entry"]) & (c < sma)).to_numpy()
    rv, cv = rsi.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, last_low, trail = 0, np.nan, np.nan
    for i in range(m):
        held = pos == -1
        if enter[i]:
            trail, last_low = np.nan, np.nan
        if held:
            if np.isnan(last_low) or cv[i] < last_low:
                last_low = cv[i]
                trail = cv[i]
        exit_ = (not np.isnan(trail) and cv[i] > trail) or rv[i] >= p["rsi_stop"] or rv[i] <= p["rsi_take_profit"]
        if held and exit_:
            pos = 0
        elif not held and enter[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
