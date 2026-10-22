"""RSI 2 dips with a weekly RSI filter, 1-hour bars, long only: the 2-bar WMA of RSI 2 crossing under 10, with the last completed week's RSI 2 under 30 and no range spike (the bar's true range under twice
the ATR 14), goes long; the last completed day's smoothed RSI 4 above 70 closes.
Port of FMZ strategy #441158 "高级RSI指标交易策略Advanced-RSI-Indicator-Trading-Strategy" (S&P500 RSI2 Studio).

FMZ source id: 441158

Source
    https://www.fmz.com/strategy/441158 (PineScript v5, FMZ last modified 2024-02-06 11:47:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 207-263), base RSI 2, entry level 10, exit 70; weekly RSI 2 filter on (30); MA filter off; exit / daily RSI 4 (daily unused); 2nd RSI filter off; ATR filter on (14, x 2)
    weeklyRsi = security("W", wma(rsi(close, 2), 1));  exitRsi = security("D", wma(rsi(close, 4), 2));  vrsi = wma(rsi(close, 2), 2)
    buy = crossunder(vrsi, 10) and weeklyRsi < 30 and not (atr(1) >= atr(14) x 2) -> entry;  exitRsi > 70 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() without lookahead is read as the last completed higher bar: the
      weekly RSI 2 of the previous broker week (Monday to Friday by broker-day label) and the daily
      smoothed RSI 4 of the previous broker day, built from the module's own bars. atr(1) is the bar's true
      range. The MA and second RSI filters are off; dailyRsi is never used. Long only. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly and daily values from completed periods.
    2 generic: PASS, RSI 2 cross, weekly RSI filter and range filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441158_rsi2_dip_weekly_rsi_filter_daily_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "over_sold": [10, 20],
    "weekly_over_sold": [30, 50],
}
DEFAULT_PARAMS = {"over_sold": 10, "weekly_over_sold": 30, "base_length": 2, "weekly_rsi_length": 2,
                  "exit_rsi_length": 4, "over_bought_exit": 70, "num_atr": 14, "atr_factor": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wr = _rsi(c.groupby(week).last(), int(p["weekly_rsi_length"])).shift(1)    # last completed week
    w_rsi = pd.Series(wr.reindex(week).to_numpy(), index=c.index)
    dr = _wma(_rsi(c.groupby(day).last(), int(p["exit_rsi_length"])), 2).shift(1)   # last completed day
    x_rsi = pd.Series(dr.reindex(day).to_numpy(), index=c.index)
    vrsi = _wma(_rsi(c, int(p["base_length"])), 2)
    os_ = float(p["over_sold"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    spike = tr >= _rma(tr, int(p["num_atr"])) * float(p["atr_factor"])
    buy = ((vrsi < os_) & (vrsi.shift(1) >= os_) & (w_rsi < float(p["weekly_over_sold"])) & ~spike).to_numpy()
    ex = (x_rsi > float(p["over_bought_exit"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0
    for i in range(m):
        if held == 1 and ex[i]:
            lx[i], held = True, 0
        elif held == 0 and buy[i] and i + 1 < m:
            le[i], held = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
