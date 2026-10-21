"""Kwan NRP direction, broker days: the 2-value average of stochastic(open) x RSI(open) / momentum rising is long, falling short, unchanged flat (close all); reversing.
Port of FMZ strategy #437651 "Momentum Trend Tracking Strategy" (KNRP).

FMZ source id: 437651

Source
    https://www.fmz.com/strategy/437651 (PineScript v4, FMZ last modified 2024-01-04 15:28:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-168), momentum 9, RSI 9 (of the open), stochastic 9 (of the open), NRP average 2; reverse off
    xMom = close / close[9] x 100;  val = stoch(open, high, low, 9) x rsi(open, 9) / xMom pushed to an array when xMom != 0;  avr = mean of the last 2 pushed values (once more than 2 are held)
    pos = 1 if avr > avr[1], -1 if avr < avr[1], else 0;  entry Long / Short on possig, close_all on 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The array starts with one na element, so avr exists once two values were pushed; values are pushed
      only on bars where the momentum is defined and non-zero, as written (an undefined stochastic or RSI
      pushes na). The stochastic length is hard-coded 9 in the script (its input is unused). State 0
      closes. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dimensionless oscillator product.
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

NAME = "fmz_437651_kwan_nrp_direction"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_momentum": [9, 14],
    "length_rsi": [9, 14],
}
DEFAULT_PARAMS = {"length_momentum": 9, "length_rsi": 9, "length_stoch": 9, "length_nrp": 2, "reverse": False}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    mom = (c / c.shift(int(p["length_momentum"])) * 100).to_numpy()
    r = _rsi(o, int(p["length_rsi"]))
    n = int(p["length_stoch"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (o - ll) / (hh - ll).where(hh > ll)
        val = (st * r).to_numpy() / mom
    k = int(p["length_nrp"])
    m = len(c)
    arr = [np.nan]
    avr = np.full(m, np.nan)
    for i in range(m):
        if not np.isnan(mom[i]) and mom[i] != 0:
            arr.append(val[i])
        avr[i] = sum(arr[-k:]) / k if len(arr) > k else 0.0
    a1 = np.concatenate(([np.nan], avr[:-1]))
    with np.errstate(invalid="ignore"):
        pos = np.where(avr > a1, 1.0, np.where(avr < a1, -1.0, 0.0))
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
