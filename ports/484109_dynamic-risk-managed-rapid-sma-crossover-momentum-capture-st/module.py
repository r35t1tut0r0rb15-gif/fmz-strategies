"""Momentum state entries (MACD 5 / 13 / 3, RSI 10, SMA 5 / 20) with a 1.2 ATR stop and a 2.5 ATR target, two-day bars:
every bar with MACD above its signal, RSI above 45, the close above SMA 5 and SMA 5 above SMA 20 is a long entry; the
bearish mirror is a short entry; each trade has a stop 1.2 ATR and a target 2.5 ATR from the signal close.
Port of FMZ strategy #484109 "动态风险管理的快速均线交叉动量捕捉策略-Dynamic-Risk-Managed-Rapid-SMA-Crossover-Momentum-Capture-Strategy" (Stock & Options Hyper-Scalper).

FMZ source id: 484109

Source
    https://www.fmz.com/strategy/484109 (PineScript v5, FMZ last modified 2025-02-28 10:29:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 153-194), SMA 5 / 20, RSI 10 (45 / 55), MACD 5 / 13 / 3, ATR 10, SL 1.2, TP 2.5
    long = macd > signal and rsi > 45 and close > sma5 and sma5 > sma20 -> entry (risk qty) + exit(stop = close -
    1.2 ATR, limit = close + 2.5 ATR);  short = macd < signal and rsi < 55 and close < sma5 and sma5 < sma20 (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every condition bar is an entry; the bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop
      = tp_mult x ATR / close, shifted one bar inside stops() and re-based on the fill (house rule). Consecutive signal
      bars while held re-place it: mark trailing_stop_pending; the port keeps the entry's bracket.
    * The risk-based quantity is sizing (quoted). Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs
      {} (D4). Two-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D"
      from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, oscillators and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484109_momentum_state_atr_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.2, 2.0],
    "tp_mult": [2.5, 4.0],
}
DEFAULT_PARAMS = {"rsi_len": 10, "rsi_os": 45, "rsi_ob": 55, "atr_len": 10, "sl_mult": 1.2, "tp_mult": 2.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s5, s20 = c.rolling(5).mean(), c.rolling(20).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=5, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=3, adjust=False).mean()
    long_e = ((macd > sig) & (rsi > p["rsi_os"]) & (c > s5) & (s5 > s20)).astype(bool)
    short_e = ((macd < sig) & (rsi < p["rsi_ob"]) & (c < s5) & (s5 < s20)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
