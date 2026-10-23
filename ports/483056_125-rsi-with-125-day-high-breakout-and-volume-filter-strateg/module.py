"""Broker days: on a day with volume over twice the previous day's, RSI 14 crossing over 30 goes long and RSI crossing under 70 goes short; a close crossing under the 125-bar high (which includes the bar itself) also goes short; the opposite signal reverses.
Port of FMZ strategy #483056 "相对强弱指数与125日高点突破及成交量过滤策略-RSI-with-125-Day-High-Breakout-and-Volume-Filter-Strategy" (RSI Strategy with 125-Day High and Volume Filter).

FMZ source id: 483056

Source
    https://www.fmz.com/strategy/483056 (PineScript v6, FMZ last modified 2025-02-21 11:15:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 101-143), RSI 14 (30 / 70); highest(high, 125); volume > 2 x volume[1]
    crossover(rsi, 30) and volume_increased -> entry RsiLE;  crossunder(rsi, 70) and volume_increased -> entry RsiSE
    crossover(close, highest(high, 125)) and volume_increased -> entry BuyHigh125;  crossunder(close, highest(high, 125)) and volume_increased -> entry SellHigh125

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 125-bar high includes the current bar, so a close can never cross over it: BuyHigh125 never
      fires (weird case); the cross under needs the previous close to have been the 125-bar high (a close
      at the bar's high), which happens. Default pyramiding: a second long id while long adds nothing.
      Later calls win on a two-sided bar. Entries only; an opposite entry reverses. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI band crossings and 125-day-high failures on doubled volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against twice the previous day's; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483056_rsi_band_cross_125_high_fail_volume_double_reversal"
FAMILY = "rsi_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "high_len": [125, 250],
    "vol_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"high_len": 125, "vol_mult": 2.0}


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
    h, c, v = bars_df["high"], bars_df["close"], bars_df["volume"]
    r = _rsi(c, 14)
    hh = h.rolling(int(p["high_len"])).max()
    vol_ok = v > float(p["vol_mult"]) * v.shift(1)
    rsi_le = (r > 30) & (r.shift(1) <= 30) & vol_ok
    rsi_se = (r < 70) & (r.shift(1) >= 70) & vol_ok
    hi_le = (c > hh) & (c.shift(1) <= hh.shift(1)) & vol_ok      # never true (hh includes the bar)
    hi_se = (c < hh) & (c.shift(1) >= hh.shift(1)) & vol_ok
    # order of calls: RsiLE, RsiSE, BuyHigh125, SellHigh125; the last true call sets the side
    sell = hi_se | (rsi_se & ~hi_le)
    buy = (hi_le | (rsi_le & ~rsi_se)) & ~hi_se
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
