"""Wilder's Volatility System, broker days: the close crossing over the previous stop-and-reverse level (lowest close of 9 + 1.8 ATR(9)) goes long, crossing under the previous lower level (highest close of
9 - 1.8 ATR) goes short; always in the market after the first signal; reversing.
Port of FMZ strategy #442122 "Volatility Breakout Reversal Trading Strategy" (Volatility System [Strat]).

FMZ source id: 442122

Source
    https://www.fmz.com/strategy/442122 (PineScript v3, FMZ last modified 2024-02-19 15:12:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-211), ATR 9; ARC factor 1.8; longs only / shorts only off; dates 2000-9999 (always allowed); 100 % of equity, capital 100000, commission 0.1
    SarLo = highest(close, 9) - 1.8 atr(9);  SarHi = lowest(close, 9) + 1.8 atr(9)
    EnterLong = not InLong[1] and crossover(close, SarHi[1]) -> entry Long;  EnterShort = not InShort[1] and crossunder(close, SarLo[1]) -> entry Short;  InLong / InShort follow the previous bar's entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * The in-position flags are ported as written (set from the previous bar's entries). strategy.entry
      reverses: REVERSAL INTENDED. The 100 % of equity size, capital and commission are sizing. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR stop-and-reverse levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442122_wilder_volatility_system_sar_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_length": [9, 14],
    "arc_factor": [1.8, 2.8],
}
DEFAULT_PARAMS = {"atr_length": 9, "arc_factor": 1.8}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["atr_length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    arc = _rma(tr, n) * float(p["arc_factor"])
    sar_lo = c.rolling(n).max() - arc
    sar_hi = c.rolling(n).min() + arc
    xo = ((c > sar_hi.shift(1)) & (pc <= sar_hi.shift(2))).to_numpy()
    xu = ((c < sar_lo.shift(1)) & (pc >= sar_lo.shift(2))).to_numpy()
    m = len(c)
    el, es = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_l = in_s = False
    for i in range(m):
        el[i] = (not in_l) and xo[i]
        es[i] = (not in_s) and xu[i]
        el1 = el[i - 1] if i > 0 else False
        es1 = es[i - 1] if i > 0 else False
        in_l, in_s = (in_l and not es1) or el1, (in_s and not el1) or es1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    le = pd.Series(el, index=ix)
    return le, false, pd.Series(es, index=ix) & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
