"""EMA 9 / 21 / 63 / 200 stacked upward with the close over the EMA 9 and RSI 14 at or under 60, broker days, long only: the state goes long; the EMA 21 crossing under the EMA 63 closes.
Port of FMZ strategy #490914 "多重指数移动平均线趋势确认与RSI过滤入场策略-Multiple-EMA-Trend-Confirmation-with-RSI-Entry-Filter-Strategy" (4 EMAs with Entry and Exit Strategy).

FMZ source id: 490914

Source
    https://www.fmz.com/strategy/490914 (PineScript v5, FMZ last modified 2025-04-17 14:33:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-214), EMA 9 / 21 / 63 / 200; RSI 14 / 60; capital 1000000, 10 % of equity, commission 0.75 %
    ema9 > ema21 > ema63 > ema200 and close > ema9 and rsi <= 60 -> entry Long;  crossunder(ema21, ema63) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a state and repeats while held (ignored then). Long only. The commission is a cost.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA-stack state with an RSI cap and an EMA-cross exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity, capital and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490914_ema9_21_63_200_stack_rsi60_ema21_63_exit_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_cap": [60, 70],
    "exit_slow": [63, 100],
}
DEFAULT_PARAMS = {"rsi_cap": 60, "exit_slow": 63}


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
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    e9, e21, e63, e200 = ema(9), ema(21), ema(p["exit_slow"]), ema(200)
    le = (e9 > e21) & (e21 > e63) & (e63 > e200) & (c > e9) & (_rsi(c, 14) <= float(p["rsi_cap"]))
    lx = (e21 < e63) & (e21.shift(1) >= e63.shift(1)) & ~le
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
