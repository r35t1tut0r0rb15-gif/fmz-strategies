"""EMA 9 / 21 crosses confirmed by RSI 14 and the MACD side, with a 1 % stop / 2 % target from the entry, two-day
bars: EMA 9 crossing above EMA 21 with RSI below 70 and MACD above its signal goes long; the mirror (RSI above 30, MACD
below its signal) goes short.
Port of FMZ strategy #483124 "多重指标交叉智能型趋势交易策略-Multi-Indicator-Cross-Intelligence-Trend-Trading-Strategy" (BTCUSD Intraday - AI-like Strategy).

FMZ source id: 483124

Source
    https://www.fmz.com/strategy/483124 (PineScript v5, FMZ last modified 2025-02-27 16:54:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 143-198), EMA 9 / 21, RSI 14, MACD 12 / 26 / 9, TP 2 %, SL 1 %
    long = crossover(ema9, ema21) and rsi < 70 and macd > signal (short mirrored)
    while held: exit(stop = avg_price x (1 -+ 1 %), limit = avg_price x (1 +- 2 %)) on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits use strategy.position_avg_price (the fill) on every bar while held: a fixed 1 % / 2 % bracket from the
      fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
    * Two-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the
      backtest header ("Intraday" and "BTCUSD" in the title are labels). Stops on two-day bars: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed bracket from the fill.
    2 generic: PASS, moving averages, RSI, MACD and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483124_ema9_21_rsi_macd_pct_bracket_2d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "sl_pct": 1.0, "tp_pct": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi < 70) & (macd > sig)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi > 30) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
