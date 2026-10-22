"""EMA 9 / 21 crossings with RSI 14 under 70 / over 30, broker days: the up-cross goes long, the down-cross goes short; reversing, no other exit.
Port of FMZ strategy #483116 "双均线交叉结合RSI动量优化交易策略-Dual-Moving-Average-Crossover-with-RSI-Momentum-Enhancement-Strategy" (Ausiris Gold Trading Strategy).

FMZ source id: 483116

Source
    https://www.fmz.com/strategy/483116 (PineScript v6, FMZ last modified 2025-02-27 16:57:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-147), EMA 9 / 21; RSI 14 / 70 / 30; MPL 2.0 notice (McTunT)
    crossover(ema9, ema21) and rsi < 70 -> entry Long;  crossunder(ema9, ema21) and rsi > 30 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only: each reverses the other side (REVERSAL INTENDED), no other exit. No sizing code. The
      MPL 2.0 notice is kept with the verbatim copy (ported, stated). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an RSI filter.
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

NAME = "fmz_483116_ema9_21_cross_rsi14_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [9, 5],
    "slow_length": [21, 50],
}
DEFAULT_PARAMS = {"fast_length": 9, "slow_length": 21, "rsi_length": 14, "rsi_ob": 70, "rsi_os": 30}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < float(p["rsi_ob"]))
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > float(p["rsi_os"]))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
