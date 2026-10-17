"""RSI 2 turning up from below 25 above SMA 50, from flat, held for a fixed number of bars, long only, daily
(broker-day) bars: the previous RSI(2) below 25, RSI rising and the close above SMA 50 go long; the position closes on
the 5th bar counted from the signal bar (the exit acts at the next open).
Port of FMZ strategy #482838 "基于RSI2的动态突破交易策略结合移动平均线过滤系统-RSI2-Based-Dynamic-Breakout-Trading-Strategy-with-Moving-Average-Filter-System" (RSI 2 Strategy with Fixed Lines and Moving Average Filter).

FMZ source id: 482838

Source
    https://www.fmz.com/strategy/482838 (PineScript v6, FMZ last modified 2025-02-27 17:37:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-140), RSI 2, buy level 25, hold 5 bars, SMA 50 filter on
    buy = rsi[1] < 25 and rsi > rsi[1] and position_size == 0 and close > sma50, with no count running ->
    entry, barsHeld = 0; then barsHeld += 1 on every bar (the signal bar included); barsHeld >= 5 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The count starts on the signal bar, so the close is signalled 4 bars later (held for 4 bars from the fill), as
      written. Entries only from flat and while no count runs: plain state machine. Long only; no stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, a moving average and a bar count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482838_rsi2_turn_up_sma50_time_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_bars": [5, 10],
    "use_ma_filter": [True, False],
}
DEFAULT_PARAMS = {"rsi_len": 2, "buy_level": 25.0, "max_bars": 5, "ma_len": 50, "use_ma_filter": True}


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
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    ma_ok = (c > c.rolling(int(p["ma_len"])).mean()) if p["use_ma_filter"] else pd.Series(True, index=c.index)
    cond = ((rsi.shift(1) < p["buy_level"]) & (rsi > rsi.shift(1)) & ma_ok).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, count = 0, None
    k = int(p["max_bars"])
    for i in range(m):
        pos = held
        if cond[i] and held == 0 and count is None and i + 1 < m:
            le[i], pos, count = True, 1, 0
        if count is not None:
            count += 1
            if count >= k:
                lx[i] = not le[i]
                count = None
                pos = 0
        held = pos
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
