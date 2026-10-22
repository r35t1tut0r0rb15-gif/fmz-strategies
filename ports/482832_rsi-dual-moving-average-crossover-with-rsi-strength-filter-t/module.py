"""EMA 5 / SMA 10 up-crossings, 3-day bars, long only: an up-cross while the buy flag is off goes long; with the flag on, a down-cross or RSI 14 under 50 closes and clears the flag.
Port of FMZ strategy #482832 "双均线交叉结合RSI强弱过滤交易策略-Dual-Moving-Average-Crossover-with-RSI-Strength-Filter-Trading-Strategy" (EMA and SMA Crossover with RSI14 Filtering).

FMZ source id: 482832

Source
    https://www.fmz.com/strategy/482832 (PineScript v5, FMZ last modified 2025-02-20 14:50:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-226), EMA 5; SMA 10; RSI 14; levels 60 / 50
    crossover(ema5, sma10) and not active_buy -> (close < rsi14 ? [close > rsi14 -> entry Buy] : entry Buy), active_buy := true
    crossunder(ema5, sma10) and not active_sell -> (close > rsi14 ? [close < rsi14 -> entry Sell] : entry Sell), active_sell := true
    active_buy and (crossunder(ema5, sma10) or rsi14 < 50) -> close Buy, active_buy := false;  active_sell and (crossover or rsi14 > 60) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the "RSI 60 / 50" tests compare the close (a price) with the RSI value (0-100). At the
      header's ETH_USDT prices the close is always above it, so the buy branch always enters and the
      sell branch never does (its inner test can never be true): the port drops the comparison and has
      no shorts, read at the header's prices like other price units (#440456). Long only.
    * The flags are followed in a loop as written: a close called while the entry is still pending (the
      flag set on this bar) closes nothing and clears the flag, so that long stays open until a later
      up-cross sets the flag again and an exit condition holds. A repeat entry while long adds nothing.
    * No sizing code. Bars are blocks of three broker days (17:00 America/New_York) counted from
      1970-01-01, stamped with their first minute. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the close-vs-RSI test read at the header's prices (always passes; no shorts).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482832_ema5_sma10_cross_rsi14_50_exit_flag_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 8],
    "slow": [10, 20],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 10, "rsi_length": 14, "exit_level": 50, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    weak = (r < float(p["exit_level"])).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag = pos = False
    pend_in = pend_out = False
    for i in range(m):
        if pend_in:
            pos, pend_in = True, False
        if pend_out:
            pos, pend_out = False, False
        if up[i] and not flag:
            flag = True
            if not pos:
                le[i], pend_in = True, True
        if flag and (dn[i] or weak[i]):
            flag = False
            if pos:
                lx[i], pend_out = True, True
                if le[i]:
                    le[i], pend_in = False, False
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
