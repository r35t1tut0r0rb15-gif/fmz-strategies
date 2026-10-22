"""Close crossings of a one-step ATR line (close -/+ ATR 10 by the side of the close against the line's last value), broker days: crossing up goes long, crossing down goes short; reversing.
Port of FMZ strategy #484773 "动态ATR追踪止损交易策略市场波动性自适应系统-Dynamic-ATR-Trailing-Stop-Trading-Strategy-Market-Volatility-Adaptive-System" (Xfera Trading Bot Automation).

FMZ source id: 484773

Source
    https://www.fmz.com/strategy/484773 (PineScript v5, FMZ last modified 2025-03-04 11:03:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 199-239), key value 1; ATR 10; Heikin Ashi source off; 10 % of equity
    line = close > nz(line[1], 0) ? close - atr : close + atr;  crossover(close, line) -> close Sell, entry Buy;  crossunder -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is not ratcheted (no max / min with its last value), as written; the first bar compares
      with 0. The Heikin Ashi option is off by default. Each crossing closes the other side and enters:
      REVERSAL INTENDED. The 10 % of equity size is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR line crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_484773_atr10_flip_line_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key_value": [1.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"key_value": 1.0, "atr_period": 10}


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
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    nl = (float(p["key_value"]) * _rma(tr, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ln = np.full(m, np.nan)
    for i in range(m):
        prev = ln[i - 1] if i >= 1 and not np.isnan(ln[i - 1]) else 0.0      # nz(line[1], 0)
        ln[i] = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
    line = pd.Series(ln, index=c.index)
    le = (c > line) & (c.shift(1) <= line.shift(1))
    se = (c < line) & (c.shift(1) >= line.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
