"""EMA 20 / 50 crosses with an RSI cap and an ATR bracket, two-day bars: EMA 20 crossing above EMA 50 with RSI 14
below 70 and the close above EMA 50 goes long; the mirror (RSI above 30) goes short; each trade has a stop 1 ATR and
a target 2 ATR away.
Port of FMZ strategy #489650 "动态波动率自适应EMAxRSI交叉策略-Dynamic-Volatility-Adaptive-EMA-RSI-Crossover-Strategy" (Kad_Sniper).

FMZ source id: 489650

Source
    https://www.fmz.com/strategy/489650 (PineScript v5, FMZ last modified 2025-04-07 13:25:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-234), EMA 20 / 50, RSI 14 (70 / 30), ATR 14 x 1 / 2
    buy = crossover(ema20, ema50) and rsi < 70 and close > ema50;  sell = crossunder and rsi > 30 and close < ema50
    sell -> close "Buy";  buy -> close "Sell";  then entry with exit(stop = close -+ 1 ATR, limit = close +- 2 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop = 1 x ATR / close, tp_stop = 2 x ATR / close, shifted
      one bar inside stops(), re-based on the fill (house rule). The risk-based lot size is sizing.
    * The closes come before the entries: a stop-and-reverse (REVERSAL INTENDED). A buy and a sell cannot fall on one
      bar.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "2D" from the backtest header (period 2d): two-day bars from
      broker days in fixed blocks counted from 1970-01-01 (block phase: decision owed), as #426509: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 %-risk lot quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489650_ema_20_50_cross_rsi_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.0, 2.0],
    "tp_atr": [2.0, 4.0],
}
DEFAULT_PARAMS = {"short_ema": 20, "long_ema": 50, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "sl_atr": 1.0,
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
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = ((es > el) & (es.shift(1) <= el.shift(1)) & (rsi < p["rsi_ob"]) & (c > el)).astype(bool)
    sell = ((es < el) & (es.shift(1) >= el.shift(1)) & (rsi > p["rsi_os"]) & (c < el)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, 14) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
