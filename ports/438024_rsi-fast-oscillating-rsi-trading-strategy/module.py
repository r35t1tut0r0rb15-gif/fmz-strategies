"""Noro's fast RSI dip buys, broker days, long only: a red bar with a body over a quarter of its 30-bar EMA and the fast RSI (up average 2, down average 9) under 30 buys; a green bar with a body over half its
EMA and the fast RSI over 30 closes.
Port of FMZ strategy #438024 "快速震荡RSI交易策略Fast-Oscillating-RSI-Trading-Strategy" (FRSI str 1.22).

FMZ source id: 438024

Source
    https://www.fmz.com/strategy/438024 (PineScript v3, FMZ last modified 2024-01-08 11:50:38).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 147-192), RSI up period 2, down period 9, limit 30, source close; RSI bars 1; date inputs unused
    fastrsi from rma(max(change, 0), 2) and rma(-min(change, 0), 9);  up = red bar and sps == 0 and fastrsi < 30 and body > ema(body, 30) / 4 -> entry Long;  exit = green bar and fastrsi > 30 and body > ema(body, 30) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * sps is declared without var, so it is 0 on every bar when tested: no effect. The short signal (dn)
      is computed but never traded. The date inputs feed no condition. Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fast RSI levels and bar bodies.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND432219 (2 members, best partner #432219, Jaccard 0.734); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438024_noro_frsi_red_bar_dip_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [30, 20],
    "dnrsiperiod": [9, 14],
}
DEFAULT_PARAMS = {"limit": 30.0, "dnrsiperiod": 9, "uprsiperiod": 2, "body_len": 30}


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
    o, c = bars_df["open"], bars_df["close"]
    d = c.diff()
    fu = _rma(d.clip(lower=0), int(p["uprsiperiod"]))
    fd = _rma((-d).clip(lower=0), int(p["dnrsiperiod"]))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + fu / fd)
    r = r.where(fu != 0, 0.0).where(fd != 0, 100.0)     # Pine: down == 0 -> 100, else up == 0 -> 0
    r = r.where(fd.notna() & (fu.notna() | (fd == 0)))
    body = (c - o).abs()
    eb = body.ewm(span=int(p["body_len"]), adjust=False).mean()
    lim = float(p["limit"])
    up = (c < o) & (r < lim) & (body > eb / 4)
    ex = (c > o) & (r > lim) & (body > eb / 2)
    false = pd.Series(False, index=bars_df.index)
    return up, ex, false, false.copy()


def portfolio_kwargs(**params):
    return {}
