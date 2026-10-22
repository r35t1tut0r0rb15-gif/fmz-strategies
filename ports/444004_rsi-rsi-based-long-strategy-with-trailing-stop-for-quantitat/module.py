"""RSI 14 crossings, daily bars: from flat, the RSI crossing over 30 goes long and crossing under 70 goes short, each with a 5 % stop from the signal close; the RSI crossing under 70 closes either side.
Port of FMZ strategy #444004 "基于相对强弱指数RSI与止损的多头量化交易策略RSI-based-Long-Strategy-with-Trailing-Stop-for-Quantitative-Trading" (RSI Strategy (Long)).

FMZ source id: 444004

Source
    https://www.fmz.com/strategy/444004 (PineScript v5, FMZ last modified 2024-03-08 15:06:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-174), RSI 14 (30 / 70); stop 5 %; short quantity 0.001; 100 % of equity, capital 1000
    flat and crossover(rsi, 30) -> entry Long, exit(stop = close x 0.95);  flat and crossunder(rsi, 70) -> entry Short (qty 0.001), exit(stop = close x 1.05)
    crossunder(rsi, 70) -> close Long;  crossunder(rsi, 70) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short's close test is its own entry test: on the signal bar the close finds no open short, so
      the short opens and the next crossing under 70 closes it, as written. The stop is a fixed fraction
      0.05 of the fill (#437751). Entries come only from flat. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: mark coarse_bar_stop. The short's 0.001 quantity, the percent-of-equity
      size and capital are sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, RSI level crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantities and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_444004_rsi14_cross_flat_entries_pct_stop"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 7],
    "percent_diff": [5, 10],
}
DEFAULT_PARAMS = {"length": 14, "percent_diff": 5, "over_sold": 30, "over_bought": 70}


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
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))
    os_, ob = float(p["over_sold"]), float(p["over_bought"])
    co = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    cu = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    s_ = float(p["percent_diff"]) / 100
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        elif pos == -1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + s_):
            pos = 0
        if pos == 0 and i + 1 < m and co[i]:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 0 and i + 1 < m and cu[i]:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == 1 and i >= entry_i and cu[i]:
            lx[i], pos = True, 0
        elif pos == -1 and i >= entry_i and cu[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["percent_diff"]) / 100}


def portfolio_kwargs(**params):
    return {}
