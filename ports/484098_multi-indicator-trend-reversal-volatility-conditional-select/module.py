"""Counter-trend band fades inside the trend, outside strong trends, in a 09:20-15:15 window, with a 2 ATR stop and a
3.5 ATR target, 1-hour bars: with EMA 50 below EMA 200, RSI 14 above 65, the close at or above the 1.8-sigma upper band,
ADX 14 at most 35 and ATR above half its 10-bar average, inside the window, the strategy goes short ("sell call"); the
bullish mirror goes long ("sell put").
Port of FMZ strategy #484098 "多指标趋势反转波动率条件选择性期权销售策略-Multi-Indicator-Trend-Reversal-Volatility-Conditional-Selective-Options-Selling-Strategy" (Nifty BankNifty Option Selling Strategy).

FMZ source id: 484098

Source
    https://www.fmz.com/strategy/484098 (PineScript v5, FMZ last modified 2025-02-28 10:04:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-238), EMA 50 / 200, DMI 14 / 14 (ADX <= 35), BB 20 x 1.8, RSI 14
(65 / 35), ATR 14 > 0.5 x sma(ATR, 10), window 09:20-15:15, stop 2 ATR, target 3.5 ATR
    sellCall = ema50 < ema200 and rsi > 65 and close >= upper and adx <= 35 and atr > minATR and in window -> entry short
    sellPut = ema50 > ema200 and rsi < 35 and close <= lower and adx <= 35 and atr > minATR and in window -> entry long
    every bar: exit(stop = close -+ 2 ATR, limit = close +- 3.5 ATR) for each entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * The option legs are not modelled: sellCall is a short, sellPut a long, as the source's orders are.
    * Session open (check 9 / C6): timestamp(year, month, dayofmonth, 9, 20) / (15, 15) in the chart's time zone and the
      bar's open time between them (inclusive): UTC on the author's Binance chart (session_tz "UTC", the default) or
      Asia/Kolkata (the NSE hours of the title) as the variant.
    * The exits are re-issued every bar from the current close and ATR (moving): fixed at entry, mark
      trailing_stop_pending (sl_stop = sl_atr x ATR / close of the signal bar, tp_stop = tp_atr x ATR / close,
      shifted one bar inside stops(), re-based on the fill).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-issue marked).
    2 generic: PASS, EMAs, bands, oscillators and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entry window 09:20-15:15 in session_tz (UTC as written; Asia/Kolkata as the variant).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484098_band_fade_low_adx_window"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "Asia/Kolkata"],
    "sl_atr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "length": 14, "adx_max": 35.0, "bb_mult": 1.8, "rsi_ob": 65, "rsi_os": 35,
                  "sl_atr": 2.0, "tp_atr": 3.5}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return tr


def _adx(bars_df, n):
    """ta.dmi's ADX: rma of |DI+ - DI-| / (DI+ + DI-) x 100 over the smoothing length."""
    up, dn = bars_df["high"].diff(), -bars_df["low"].diff()
    plus = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    minus = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    tr = _rma(_tr(bars_df), n)
    pdi, mdi = 100 * _rma(plus, n) / tr, 100 * _rma(minus, n) / tr
    s = pdi + mdi
    return 100 * _rma((pdi - mdi).abs() / s.where(s != 0, 1.0), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    adx = _adx(bars_df, n)
    basis = c.rolling(20).mean()
    sd = c.rolling(20).std(ddof=0)
    up, lo = basis + p["bb_mult"] * sd, basis - p["bb_mult"] * sd
    rsi = _rsi(c, n)
    atr = _rma(_tr(bars_df), n)
    vol = atr > atr.rolling(10).mean() * 0.5
    loc = bars_df.index.tz_convert(p["session_tz"])
    hm = pd.Series(loc.hour * 60 + loc.minute, index=bars_df.index)
    inside = (hm >= 9 * 60 + 20) & (hm <= 15 * 60 + 15)
    calm = ~(adx > p["adx_max"])
    short_e = ((e50 < e200) & (rsi > p["rsi_ob"]) & (c >= up) & calm & vol & inside).astype(bool)
    long_e = ((e50 > e200) & (rsi < p["rsi_os"]) & (c <= lo) & calm & vol & inside).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_rma(_tr(bars_df), int(p["length"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_atr"] * a, "tp_stop": p["tp_atr"] * a}


def portfolio_kwargs(**params):
    return {}
