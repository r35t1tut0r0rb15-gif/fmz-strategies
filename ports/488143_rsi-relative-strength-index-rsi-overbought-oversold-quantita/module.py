"""RSI 14 band re-entries, broker days: RSI crossing back above 30 goes long and RSI crossing above 70 closes it; RSI
crossing back below 70 goes short and RSI crossing below 30 closes it.
Port of FMZ strategy #488143 "相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy" (RSI Overbought/Oversold Strategy).

FMZ source id: 488143

Source
    https://www.fmz.com/strategy/488143 (PineScript v6, FMZ last modified 2025-03-25 14:22:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-197), RSI 14, levels 30 / 70
    crossover(rsi, 30) -> entry long;  crossover(rsi, 70) -> close long
    crossunder(rsi, 70) -> entry short;  crossunder(rsi, 30) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MetaTrader alert strings (inputs written before strategy(), as FMZ accepted them) only feed alerts: not
      ported.
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); a short
      signal while long reverses (REVERSAL INTENDED). No two of the four crosses that conflict can fall on one bar.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity and the MT4 lot input quoted in original_sizing.txt.
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

NAME = "fmz_488143_rsi_band_reentry"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 21],
    "band": [30, 25],
}
DEFAULT_PARAMS = {"rsi_len": 14, "band": 30}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["rsi_len"]))
    lo, hi = float(p["band"]), 100.0 - float(p["band"])
    r1 = rsi.shift(1)
    go_l = ((rsi > lo) & (r1 <= lo)).to_numpy()
    out_l = ((rsi > hi) & (r1 <= hi)).to_numpy()
    go_s = ((rsi < hi) & (r1 >= hi)).to_numpy()
    out_s = ((rsi < lo) & (r1 >= lo)).to_numpy()
    m = len(rsi)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if go_s[i]:
            pos = -1
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
