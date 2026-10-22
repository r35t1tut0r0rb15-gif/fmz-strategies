"""RSI 14 crossings of 30 and 70, broker days: RSI crossing up through 30 goes long and up through 70 closes it; crossing down through 70 goes short and down through 30 closes it.
Port of FMZ strategy #488143 "相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy" (RSI Overbought/Oversold Strategy).

FMZ source id: 488143

Source
    https://www.fmz.com/strategy/488143 (PineScript v6, FMZ last modified 2025-03-25 14:22:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-209), RSI 14 / 30 / 70; 5 % of equity; MT4/5 alert strings (0.1 lots)
    crossover(rsi, 30) -> entry BUY;  crossover(rsi, 70) -> close BUY;  crossunder(rsi, 70) -> entry SELL;  crossunder(rsi, 30) -> close SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * An opposite entry would reverse (REVERSAL INTENDED), though each side's exit comes first in
      practice. The MetaTrader alert strings are not orders. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI threshold crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 5 % of equity and the alert lot size stored, not ported.
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

NAME = "fmz_488143_rsi14_30_70_cross_entries_exits_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [30, 20],
    "overbought": [70, 80],
}
DEFAULT_PARAMS = {"oversold": 30, "overbought": 70, "rsi_length": 14}


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
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    r1 = r.shift(1)
    os_, ob = float(p["oversold"]), float(p["overbought"])
    le = (r > os_) & (r1 <= os_)
    lx = (r > ob) & (r1 <= ob)
    se = (r < ob) & (r1 >= ob)
    sx = (r < os_) & (r1 >= os_)
    return le, lx & ~se, se, sx & ~le


def portfolio_kwargs(**params):
    return {}
