"""Three-day RSI 2 slides above the SMA 200, daily bars, long only: an RSI 2 falling three days in a row from over 60 to under 10 with the close over the SMA 200 buys; an RSI 2 over 70 sells.
Port of FMZ strategy #471672 "均线修正型RSI三重验证机会策略-Triple-Validated-RSI-Mean-Reversion-with-Moving-Average-Filter-Strategy" (Larry Connors RSI 3 Strategy).

FMZ source id: 471672

Source
    https://www.fmz.com/strategy/471672 (PineScript v5, FMZ last modified 2024-11-12 11:37:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-131), SMA 200; RSI 2; first drop from over 60; under 10 today; exit over 70 (constants)
    close > sma200 and rsi2[2] > rsi2[1] > rsi2 and rsi2[2] > 60 and rsi2 < 10 -> entry Buy;  rsi2 > 70 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and exit tests cannot hold on the same bar. Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI 2 slides in an uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471672_connors_rsi2_three_day_slide_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_th": [10, 20],
    "exit_th": [70, 50],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"entry_th": 10, "exit_th": 70, "sma_len": 200}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, 2)
    r1, r2 = r.shift(1), r.shift(2)
    le = (c > c.rolling(int(p["sma_len"])).mean()) & (r2 > r1) & (r1 > r) & (r2 > 60) & (r < float(p["entry_th"]))
    lx = r > float(p["exit_th"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
