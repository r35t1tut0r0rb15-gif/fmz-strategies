"""EMA 50 side with MACD histogram and RSI 50-70 / 30-50 filters and an ATR bracket, two-day bars: a close above EMA
50 with a positive MACD histogram and RSI between 50 and 70 is long; the mirror is short; each trade has a stop 1 ATR
and a target 2 ATR away (re-placed every bar in the source, fixed at the signal bar here).
Port of FMZ strategy #489966 "多指标协同动态风险管理短线交易策略EMAMACDRSI结合ATR自适应止损止盈技术-Multi-Indicator-Synergistic-Dynamic-Risk-Management-Scalping-Strategy-EMAMACDRSI-with-ATR-Adaptive-Stop-Loss-Take-Profit-Technique" (Scalping 15min: EMA + MACD + RSI + ATR-based SL/TP).

FMZ source id: 489966

Source
    https://www.fmz.com/strategy/489966 (PineScript v5, FMZ last modified 2025-04-10 15:27:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-245), EMA 50, MACD 12 / 26 / 9, RSI 14 (70 / 30), ATR 14 x 1 / 2
    long = close > ema and hist > 0 and 50 < rsi < 70;  short = close < ema and hist < 0 and 30 < rsi < 50
    every bar: stop / take = close -+ 1 ATR / close +- 2 ATR on the held side; exit("Exit", from_entry = "", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket follows every bar's close (a moving level): mark trailing_stop_pending. The port fixes it at the
      signal bar: sl_stop = 1 x ATR / close, tp_stop = 2 x ATR / close, shifted one bar inside stops(), re-based on
      the fill.
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). The title's "15min" is a label.
    * FREQ = "2D" from the backtest header (period 2d): two-day bars built from broker days (session ending 17:00
      New York), in fixed blocks of two broker-day dates counted from 1970-01-01 (block phase: decision owed), stamped
      with the first session start (as #426509): coarse_bar_stop. Stop module: portfolio_kwargs {} (D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, EMA, MACD, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489966_ema_macd_rsi_atr_bracket_2d"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.0, 2.0],
    "tp_atr": [2.0, 4.0],
}
DEFAULT_PARAMS = {"ema_len": 50, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "atr_len": 14, "sl_atr": 1.0,
                  "tp_atr": 2.0}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_c = ((c > ema) & (hist > 0) & (rsi > 50) & (rsi < p["rsi_ob"])).astype(bool)
    short_c = ((c < ema) & (hist < 0) & (rsi < 50) & (rsi > p["rsi_os"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
