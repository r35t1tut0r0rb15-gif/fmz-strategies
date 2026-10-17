"""EMA 50 side with MACD histogram and RSI 50-70 / 30-50 filters and an ATR bracket, 15-minute bars: a close above
EMA 50 with a positive MACD histogram and RSI between 50 and 70 is long; the mirror is short; each trade has a stop
1 ATR and a target 2 ATR away (re-placed every bar in the source, fixed at the signal bar here).
Port of FMZ strategy #489634 "多指标结合的自适应波动ATR动态止盈止损15分钟图表趋势跟踪策略-Multi-Indicator-Adaptive-Volatility-ATR-Dynamic-SL-TP-15-Minute-Chart-Trend-Following-Strategy" (Scalping 15min: EMA + MACD + RSI + ATR-based SL/TP).

FMZ source id: 489634

Source
    https://www.fmz.com/strategy/489634 (PineScript v5, FMZ last modified 2025-04-07 11:33:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-215), EMA 50, MACD 12 / 26 / 9, RSI 14 (70 / 30), ATR 14 x 1 / 2
    long = close > ema and hist > 0 and 50 < rsi < 70;  short = close < ema and hist < 0 and 30 < rsi < 50
    every bar: stop / take = close -+ 1 ATR / close +- 2 ATR on the held side; exit("Exit", from_entry = "", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same logic as #489966 (the 2-day version, without the webhook texts), on the source's 15-minute bars.
    * The bracket follows every bar's close (a moving level): mark trailing_stop_pending. The port fixes it at the
      signal bar: sl_stop = 1 x ATR / close, tp_stop = 2 x ATR / close, shifted one bar inside stops(), re-based on
      the fill.
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, EMA, MACD, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group (same logic as #489966, a different bar size); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489634_ema_macd_rsi_atr_bracket_15m"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.0, 2.0],
    "tp_atr": [2.0, 4.0],
}
DEFAULT_PARAMS = {"ema_len": 50, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "atr_len": 14, "sl_atr": 1.0,
                  "tp_atr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
