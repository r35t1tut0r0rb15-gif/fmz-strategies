"""EMA 6 / EMA 2 crosses with a MACD (18 / 19 / 24) filter and a 7 ATR bracket, two-day bars: EMA 6 crossing above EMA 2
with MACD above its signal and above zero goes long; the mirror goes short; each trade has a stop and a target 7 ATR
from the signal close.
Port of FMZ strategy #488004 "多指标动态趋势跟踪交易系统EMA交叉MACD动量过滤ATR风险管理策略-Multi-Indicator-Dynamic-Trend-Following-Trading-System-EMA-Crossover-MACD-Momentum-Filter-ATR-Risk-Management-Strategy" (3-7 Program EMA + MACD + ATR).

FMZ source id: 488004

Source
    https://www.fmz.com/strategy/488004 (PineScript v5, FMZ last modified 2025-03-24 13:08:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 141-177), EMA "short" 6 / "long" 2, MACD 18 / 19 / 24, ATR 13 x 7
    long = crossover(ema6, ema2) and macd > signal and macd > 0;  short = crossunder(ema6, ema2) and macd < signal
    and macd < 0;  entry + exit(limit = close +- 7 ATR, stop = close -+ 7 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA lengths are kept as written (the "short" EMA is the slower one).
    * The bracket is fixed at the signal bar: sl_stop = tp_stop = atr_mult x ATR / close, shifted one bar inside
      stops() and re-based on the fill (house rule). A same-side signal while held re-places it: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, EMAs, MACD and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488004_ema6_2_cross_macd_7atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [7.0, 3.0],
    "short_len": [6, 9],
}
DEFAULT_PARAMS = {"short_len": 6, "long_len": 2, "atr_len": 13, "atr_mult": 7.0, "macd_fast": 18, "macd_slow": 19,
                  "macd_signal": 24}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    macd = (c.ewm(span=int(p["macd_fast"]), adjust=False).mean()
            - c.ewm(span=int(p["macd_slow"]), adjust=False).mean())
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    long_e = ((a > b) & (a.shift(1) <= b.shift(1)) & (macd > sig) & (macd > 0)).astype(bool)
    short_e = ((a < b) & (a.shift(1) >= b.shift(1)) & (macd < sig) & (macd < 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": d, "tp_stop": d.copy()}


def portfolio_kwargs(**params):
    return {}
