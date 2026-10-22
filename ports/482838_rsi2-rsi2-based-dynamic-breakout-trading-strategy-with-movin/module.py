"""RSI 2 turning up from under 25 above the SMA 50, broker days, long only from flat: the long is closed by an exit signal on the fifth bar counted from the signal bar.
Port of FMZ strategy #482838 "基于RSI2的动态突破交易策略结合移动平均线过滤系统-RSI2-Based-Dynamic-Breakout-Trading-Strategy-with-Moving-Average-Filter-System" (RSI 2 Strategy with Fixed Lines and Moving Average Filter).

FMZ source id: 482838

Source
    https://www.fmz.com/strategy/482838 (PineScript v6, FMZ last modified 2025-02-27 17:37:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-140), RSI 2; buy level 25; hold 5 bars; SMA 50 filter on
    rsi[1] < 25 and rsi > rsi[1] and flat and close > sma50 and na(barsHeld) -> entry Buy, barsHeld := 0
    barsHeld += 1 each bar;  barsHeld >= 5 -> close Buy, barsHeld := na

Interpretation choices (Pine rules in SURVEY_README.md)
    * barsHeld becomes 1 on the signal bar, so the close is called on the fourth bar after it and fills
      at the next open (four bars held from the fill). A new entry needs the position flat at the bar's
      close, so the first possible re-entry is on the bar the close fills. The time exit is an explicit
      exit signal, not a time stop. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI 2 turn with an SMA filter and a bar-count exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_482838_rsi2_turn_from_25_sma50_hold5_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_buy_level": [25.0, 10.0],
    "max_bars": [5, 3],
}
DEFAULT_PARAMS = {"rsi_buy_level": 25.0, "max_bars": 5, "rsi_period": 2, "ma_period": 50}


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
    r = _rsi(c, int(p["rsi_period"]))
    ma = c.rolling(int(p["ma_period"])).mean()
    buy = ((r.shift(1) < float(p["rsi_buy_level"])) & (r > r.shift(1)) & (c > ma)).to_numpy()
    mb = int(p["max_bars"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = pend_in = pend_out = False
    held = None
    for i in range(m):
        if pend_in:
            pos, pend_in = True, False
        if pend_out:
            pos, pend_out = False, False
        if buy[i] and not pos and not pend_in and held is None:
            le[i], pend_in, held = True, True, 0
        if held is not None:
            held += 1
        if held is not None and held >= mb:
            lx[i], pend_out, held = True, True, None
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
