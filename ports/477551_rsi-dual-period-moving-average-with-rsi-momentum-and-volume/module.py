"""Broker days, long only: a close above the SMA 21 with RSI 13 above its 13-bar average and volume above its 21-day average goes long; the long closes when the close crosses under the SMA 55 or the RSI crosses under its average.
Port of FMZ strategy #477551 "双周期移动平均线结合RSI动量和成交量的趋势跟踪策略-Dual-Period-Moving-Average-with-RSI-Momentum-and-Volume-Trend-Following-Strategy" (21/55 MA with RSI Crossover).

FMZ source id: 477551

Source
    https://www.fmz.com/strategy/477551 (PineScript v5, FMZ last modified 2025-01-06 13:45:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 112-159), SMA 21 / 55; RSI 13 and its SMA 13; volume SMA 21
    buy_condition = close > ma21 and rsi > rsi_avg and volume > vol_ma -> entry Buy
    sell_condition = crossunder(close, ma55) or crossunder(rsi, rsi_avg) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a state. The close acts only on a position the bar's entry leaves unchanged: a close
      crossing under the SMA 55 on an entry bar from flat keeps the new long; while long it closes it
      (an entry while long adds nothing). After a close the strategy re-enters on the next qualifying
      bar. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend-and-momentum state entries on volume with MA / RSI crossing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 21; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477551_sma21_rsi_avg_volume_state_sma55_exit_long_only"
FAMILY = "trend_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 13],
    "slow": [55, 89],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 55, "rsi_len": 13, "vol_len": 21}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    nr = int(p["rsi_len"])
    r = _rsi(c, nr)
    ra = r.rolling(nr).mean()
    buy = ((c > f) & (r > ra) & (v > v.rolling(int(p["vol_len"])).mean())).to_numpy()
    sell = (((c < s) & (c.shift(1) >= s.shift(1))) | ((r < ra) & (r.shift(1) >= ra.shift(1)))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0:
            if buy[i]:
                le[i], pos = True, 1
        elif sell[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
