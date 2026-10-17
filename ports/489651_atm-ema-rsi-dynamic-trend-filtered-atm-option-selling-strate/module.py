"""EMA 9 / 15 crosses on either side of the SMA 50 / 80 with an RSI 50 filter, short only as written, with an ATR
bracket, broker days: a bearish cross below both SMAs with RSI < 50 ("sell call") and a bullish cross above both with
RSI > 50 ("sell put") both open SHORT positions; each has a stop and a target equally far (points in the source).
Port of FMZ strategy #489651 "动态趋势过滤ATM期权卖出策略结合EMA交叉与RSI动量确认-Dynamic-Trend-Filtered-ATM-Option-Selling-Strategy-with-EMA-Crossover-and-RSI-Momentum-Confirmation" (ATM Option Selling Strategy).

FMZ source id: 489651

Source
    https://www.fmz.com/strategy/489651 (PineScript v5, FMZ last modified 2025-04-07 13:29:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-219), EMA 9 / 15, SMA 50 / 80, RSI 14, TP = SL = 50 points (point = 100 ticks)
    sellCall = close < sma50 and close < sma80 and crossunder(ema9, ema15) and rsi < 50 -> entry SHORT
    sellPut = close > sma50 and close > sma80 and crossover(ema9, ema15) and rsi > 50 -> entry SHORT
    each with exit(limit = close - 50 points, stop = close + 50 points);  hour == 15 and minute == 24 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written both conditions call strategy.short (the option legs are not modelled): short only.
    * Criterion 2: the 50-point distances become tp_atr / sl_atr x Wilder ATR(14) of the signal bar: on the author's
      daily DOGE_USDT (tick 0.00001 at about 0.17) 50 points are 0.05, about 30 %, about 5 daily ATR (judgement
      before any backtest). Shifted one bar inside stops(), re-based on the fill (house rule).
    * Session open (check 9 / C6): the 15:24 exit (in the chart's time zone) never matches a daily bar, which opens at
      the broker-day start: never fires as written; not emitted.
    * A short signal while short is ignored. Opposite entries cannot occur (no long entry exists).
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, point distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed 375 quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: a 15:24 close-all in the chart's time zone (NSE-style), never on daily bars as written; not emitted.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489651_ema_cross_both_sides_short_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bracket_atr": [5.0, 2.0],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 15, "ma_mid": 50, "ma_long": 80, "rsi_len": 14, "bracket_atr": 5.0,
                  "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e9 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    e15 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    m50, m80 = c.rolling(int(p["ma_mid"])).mean(), c.rolling(int(p["ma_long"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    dn = (e9 < e15) & (e9.shift(1) >= e15.shift(1))
    up = (e9 > e15) & (e9.shift(1) <= e15.shift(1))
    sell_call = (c < m50) & (c < m80) & dn & (rsi < 50)
    sell_put = (c > m50) & (c > m80) & up & (rsi > 50)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), (sell_call | sell_put).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["bracket_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": d.shift(1)}


def portfolio_kwargs(**params):
    return {}
