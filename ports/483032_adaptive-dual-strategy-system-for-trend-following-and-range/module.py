"""Trend or range entries switched by ADX 25, with a 1.5 ATR stop / 3 ATR target, 1-hour bars: with ADX above 25,
an SMA 50 / 200 cross with RSI and the MACD side confirming; with ADX at or below 25, a close re-crossing the lower
(upper) Bollinger band with RSI below 40 (above 60).
Port of FMZ strategy #483032 "自适应趋势跟踪与区间交易的双重策略系统-Adaptive-Dual-Strategy-System-for-Trend-Following-and-Range-Trading" (Trend vs Range Trading - Fully Fixed for v6).

FMZ source id: 483032

Source
    https://www.fmz.com/strategy/483032 (PineScript v6, FMZ last modified 2025-02-27 17:17:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-167), SMA 50 / 200, DMI 14 / 14, BB 20 x 2, RSI 14, MACD 12 / 26 / 9,
ATR 14, SL 1.5, TP 3
    trend (adx > 25): long = crossover(sma50, sma200) and rsi > 50 and macd > signal (short mirrored)
    range (adx <= 25): long = crossover(close, lower) and rsi < 40; short = crossunder(close, upper) and rsi > 60
    each entry + exit(stop = close -+ 1.5 ATR, limit = close +- 3 ATR) under its own id

Interpretation choices (Pine rules in SURVEY_README.md)
    * One position (pyramiding default): a same-side entry under the other id is ignored and its exit (from_entry that
      id) does nothing; a same-side signal under the same id re-places the bracket: mark trailing_stop_pending, the port
      keeps the entry's bracket.
    * The bracket is fixed at the signal bar: sl_stop = 1.5 ATR / close, tp_stop = 3 ATR / close, shifted one bar
      inside stops() and re-based on the fill (house rule). ADX as Pine's ta.dmi; ta.stdev population.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, ADX, Bollinger bands, RSI, MACD and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483032_adx_switch_trend_range_atr_bracket"
FAMILY = "regime_switch"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_level": [25.0, 20.0],
    "tp_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"adx_level": 25.0, "atr_len": 14, "sl_mult": 1.5, "tp_mult": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s50, s200 = c.rolling(50).mean(), c.rolling(200).mean()
    _, _, adx = _adx_pine(bars_df, 14, 14)
    trending = adx > p["adx_level"]
    ranging = ~trending & adx.notna()
    basis, dev = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    upper, lower = basis + 2 * dev, basis - 2 * dev
    rsi = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lt = trending & (s50 > s200) & (s50.shift(1) <= s200.shift(1)) & (rsi > 50) & (macd > sig)
    st = trending & (s50 < s200) & (s50.shift(1) >= s200.shift(1)) & (rsi < 50) & (macd < sig)
    lr = ranging & (c > lower) & (c.shift(1) <= lower.shift(1)) & (rsi < 40)
    sr = ranging & (c < upper) & (c.shift(1) >= upper.shift(1)) & (rsi > 60)
    short_e = (st | sr).astype(bool)
    long_e = ((lt | lr) & ~short_e).astype(bool)        # both on one bar: the later short entry wins
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
