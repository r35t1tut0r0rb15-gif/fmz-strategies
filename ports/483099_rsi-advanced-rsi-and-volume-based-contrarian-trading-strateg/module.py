"""Broker days: RSI 14 under 30 on above-average volume goes long, over 70 on above-average volume goes short; a long closes when RSI crosses over 50, a short when it crosses under 50; reversing.
Port of FMZ strategy #483099 "量化交易中基于RSI与成交量的高级反转策略-Advanced-RSI-and-Volume-Based-Contrarian-Trading-Strategy" (RSI & Volume Contrarian Strategy).

FMZ source id: 483099

Source
    https://www.fmz.com/strategy/483099 (PineScript v5, FMZ last modified 2025-02-21 13:31:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 110-172), RSI 14 (30 / 70 / 50); volume SMA 20; 10 % of equity
    longCondition = rsi < 30 and volume > volMA -> entry Long;  shortCondition = rsi > 70 and volume > volMA -> entry Short
    position_size > 0 and crossover(rsi, 50) -> close Long;  position_size < 0 and crossunder(rsi, 50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are states; an opposite entry reverses. The closes test the position held at the bar's
      close, so they act from the bar after the fill. REVERSAL INTENDED. 10 % of equity is sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes on volume with midline exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483099_rsi_extreme_volume_midline_exit_reversal"
FAMILY = "rsi_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "os": [30.0, 25.0],
    "vol_len": [20, 50],
}
DEFAULT_PARAMS = {"os": 30.0, "vol_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    os_ = float(p["os"])
    buy, sell = ((r < os_) & vol_ok).to_numpy(), ((r > 100 - os_) & vol_ok).to_numpy()
    ex_l = ((r > 50) & (r.shift(1) <= 50)).to_numpy()
    ex_s = ((r < 50) & (r.shift(1) >= 50)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
