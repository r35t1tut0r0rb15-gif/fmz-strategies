"""Two-day bars: the close crossing over a 20-bar rolling VWAP (hlc3) with RSI 20 above 30 goes long; the close crossing under it with RSI under 70 goes short; reversing.
Port of FMZ strategy #451025 "VWAP and RSI Crossover Strategy" (VWAP and RSI Strategy with Alerts).

FMZ source id: 451025

Source
    https://www.fmz.com/strategy/451025 (PineScript v4, FMZ last modified 2024-05-11 11:42:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 110-149), VWAP rolling 20; RSI 20, 70 / 30; trade qty 1
    vwapValue = sum(hlc3 x volume, 20) / sum(volume, 20);  longCondition = crossover(close, vwap) and rsi > 30 -> entry Long (qty 1);  shortCondition = crossunder and rsi < 70 -> entry Short
    strategy.exit("Exit Long", "Long", when = exitLongCondition);  strategy.exit("Exit Short", "Short", when = exitShortCondition)  (no price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are strategy.exit calls without any stop, limit or distance, so they never close
      anything (weird case): positions end only by the reversal. qty 1 is sizing. REVERSAL INTENDED.
      FREQ = "2D" from the backtest header (blocks of 2 broker days counted from 1970-01-01, each stamped
      with its first minute, as #451729).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling-VWAP crossings with RSI limits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: entry qty 1 unit, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the 20-bar rolling VWAP; exchange volume to be compared later (Austin, 2026-10-23).
Session open: blocks of 2 broker days (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451025_rolling_vwap20_cross_rsi20_2d_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vwap_period": [20, 10],
    "rsi_period": [20, 14],
}
DEFAULT_PARAMS = {"vwap_period": 20, "rsi_period": 20, "ob": 70.0, "os": 30.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, 2)


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["vwap_period"])
    sv = v.rolling(n).sum()
    vwap = ((h + lo + c) / 3 * v).rolling(n).sum() / sv.where(sv != 0)
    r = _rsi(c, int(p["rsi_period"]))
    up = (c > vwap) & (c.shift(1) <= vwap.shift(1)) & (r > float(p["os"]))
    dn = (c < vwap) & (c.shift(1) >= vwap.shift(1)) & (r < float(p["ob"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
