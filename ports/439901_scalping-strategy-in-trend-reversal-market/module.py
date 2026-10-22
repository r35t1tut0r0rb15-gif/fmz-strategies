"""Trapped counter-trend scalps, broker days: with the smoothed 60-bar stochastic of hl2 above 50, an RSI 5 above 50 and a recent RSI dip under 35 in the last 15 bars, the script goes long; the mirror goes
short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439901 "Scalping Strategy in Trend Reversal Market" (scalping against trapped countertrend).

FMZ source id: 439901

Source
    https://www.fmz.com/strategy/439901 (PineScript v4, FMZ last modified 2024-01-24 17:43:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-160), source hl2; RSI 5; stochastic 60 smoothed 13; recent window 15; levels 35 / 50; exit-if-reason-over off
    y_k = sma(stoch(hl2, high, low, 60), 13);  y_rsi = rsi(hl2, 5);  y_upper = min(y_k - 50, y_rsi - 50, 35 - lowest(y_rsi, 15));  y_upper > 0 -> entry LE
    y_lower = max(y_k - 50, y_rsi - 50, 65 - highest(y_rsi, 15));  y_lower < 0 -> entry SE;  (the reason-over closes are off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * y_upper > 0 needs the stochastic above 50 and y_lower < 0 needs it below 50, so the two cannot
      share a bar. A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic and RSI levels.
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

NAME = "fmz_439901_trapped_countertrend_scalp_state"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_b": [60, 30],
    "rsi_ct": [35.0, 25.0],
}
DEFAULT_PARAMS = {"len_b": 60, "rsi_ct": 35.0, "len_a": 5, "k_b": 13, "changk": 15, "rsi_ft": 50.0}


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
    h, lo = bars_df["high"], bars_df["low"]
    src = (h + lo) / 2
    n = int(p["len_b"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (src - ll) / (hh - ll).where(hh > ll)
    yk = st.rolling(int(p["k_b"])).mean()
    yr = _rsi(src, int(p["len_a"]))
    ck = int(p["changk"])
    ct, ft = float(p["rsi_ct"]), float(p["rsi_ft"])
    upper = pd.concat([yk - 50, yr - ft, ct - yr.rolling(ck).min()], axis=1).min(axis=1, skipna=False)
    lower = pd.concat([yk - 50, yr - ft, 100 - ct - yr.rolling(ck).max()], axis=1).max(axis=1, skipna=False)
    false = pd.Series(False, index=src.index)
    return upper > 0, false, lower < 0, false.copy()


def portfolio_kwargs(**params):
    return {}
