"""EMA 50 crosses in the EMA 200 trend with a DMI filter inside a 16:30-20:00 window and a tick bracket, 5-minute bars:
with EMA 50 above EMA 200 and DI+ above DI-, the close crossing above EMA 50 inside the window goes long; the mirror
goes short; each trade has a stop 300 ticks and a target 600 ticks from the signal close (as ATR multiples).
Port of FMZ strategy #488165 "多时段指数移动平均线交叉策略与趋势确认系统-Multi-Timeframe-Exponential-Moving-Average-Crossover-Strategy-with-Trend-Confirmation-System" (15 MIN Strategy).

FMZ source id: 488165

Source
    https://www.fmz.com/strategy/488165 (PineScript v6, FMZ last modified 2025-03-25 16:58:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 165-215), EMA 50 / 200, DMI 14 / 14, window 16:30-20:00, TP 600 / SL 300 ticks
    buy = close > ema50 and ema50 > ema200 and crossover(close, ema50) and within hours and di+ > di-
    sell = close < ema50 and ema50 < ema200 and crossunder(close, ema50) and within hours and di- > di+
    entry + exit(limit = close +- 600 ticks, stop = close -+ 300 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): hour(time) / minute(time) of the bar's open in the chart's time zone, 16:30 to
      20:00 inclusive: UTC on the author's Binance chart (session_tz "UTC", the default; the US afternoon) or
      America/New_York (DST by the zone) as the variant. The ADX threshold and the session string are unused, as
      written.
    * Criterion 2: on the author's 5-minute ETH_USDT (tick 0.01, 5-minute ATR about 6) 300 / 600 ticks are about
      0.5 / 1 Wilder ATR(14) (judgement before any backtest): sl_stop = sl_atr x ATR / close, tp_stop = 2 x that,
      fixed at the signal bar, shifted one bar inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar: mark trailing_stop_pending; the port keeps
      the entry's bracket.
    * Entries reverse (REVERSAL INTENDED); the two signals cannot fall on one bar. Stop module: portfolio_kwargs {}
      (D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: ADAPT, tick distances -> ATR multiples; EMAs and DMI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entry window 16:30-20:00 in session_tz (UTC as written; America/New_York, DST by the zone, as the variant).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488165_ema50_cross_dmi_window_bracket"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "America/New_York"],
    "sl_atr": [0.5, 1.0],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "sl_atr": 0.5, "tp_ratio": 2.0, "atr_len": 14, "di_len": 14,
                  "start_hour": 16, "start_minute": 30, "end_hour": 20, "end_minute": 0}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return tr


def _di(bars_df, n):
    """ta.dmi's DI+ and DI-: Wilder-smoothed directional movement over the smoothed true range."""
    up, dn = bars_df["high"].diff(), -bars_df["low"].diff()
    plus = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    minus = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    tr = _rma(_tr(bars_df), n)
    return 100 * _rma(plus, n) / tr, 100 * _rma(minus, n) / tr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    dip, dim = _di(bars_df, int(p["di_len"]))
    loc = bars_df.index.tz_convert(p["session_tz"])
    hm = pd.Series(loc.hour * 60 + loc.minute, index=bars_df.index)
    t0 = int(p["start_hour"]) * 60 + int(p["start_minute"])
    t1 = int(p["end_hour"]) * 60 + int(p["end_minute"])
    inside = (hm >= t0) & (hm <= t1)
    x_up = (c > e50) & (c.shift(1) <= e50.shift(1))
    x_dn = (c < e50) & (c.shift(1) >= e50.shift(1))
    long_e = ((c > e50) & (e50 > e200) & x_up & inside & (dip > dim)).astype(bool)
    short_e = ((c < e50) & (e50 < e200) & x_dn & inside & (dim > dip)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_atr"] * _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
