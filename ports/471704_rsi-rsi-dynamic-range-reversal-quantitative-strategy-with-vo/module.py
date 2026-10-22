"""Two RSI 14 crossing set-ups on one long position, daily bars, long only: the RSI crossing over 77 buys ("overbought" id), closed when it crosses under 33; the RSI crossing under 27 buys ("oversold" id), closed when it crosses over 83; one position at a time.
Port of FMZ strategy #471704 "RSI动态区间反转量化策略与波动率优化模型-RSI-Dynamic-Range-Reversal-Quantitative-Strategy-with-Volatility-Optimization-Model" (RSI Options Strategy).

FMZ source id: 471704

Source
    https://www.fmz.com/strategy/471704 (PineScript v5, FMZ last modified 2024-11-12 15:55:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-147), RSI 14; levels 80 / 30 with sensitivity 3 (77, 33, 27, 83); 10 contracts; date range always on
    crossover(rsi, 77) -> entry Buy Overbought;  crossunder(rsi, 33) -> close Buy Overbought
    crossunder(rsi, 27) -> entry Buy Oversold;  crossover(rsi, 83) -> close Buy Oversold

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default pyramiding of 1 only one of the two entries can be open; each close acts only on
      its own entry id, so the loop follows which set-up opened the long. inDateRange is fixed true.
      The 10-contract quantity is not ported. Long only. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI threshold crossings with id-specific exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471704_rsi14_two_setup_crossings_id_exits_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sensitivity": [3.0, 0.0],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"sensitivity": 3.0, "rsi_len": 14, "ob": 80.0, "os": 30.0}


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
    r = _rsi(c, int(p["rsi_len"]))
    k, ob, os_ = float(p["sensitivity"]), float(p["ob"]), float(p["os"])

    def xo(t):
        return ((r > t) & (r.shift(1) <= t)).to_numpy()

    def xu(t):
        return ((r < t) & (r.shift(1) >= t)).to_numpy()

    e_ob, x_ob, e_os, x_os = xo(ob - k), xu(os_ + k), xu(os_ - k), xo(ob + k)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = None                                  # id of the entry held into the bar
    for i in range(m):
        nxt = held
        if e_ob[i] and held is None and nxt is None:
            nxt = "ob"
        if x_ob[i] and held == "ob":
            nxt = None
        if e_os[i] and held is None and nxt is None:
            nxt = "os"
        if x_os[i] and held == "os":
            nxt = None
        if nxt is not None and held is None:
            le[i] = True
        elif nxt is None and held is not None:
            lx[i] = True
        held = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
