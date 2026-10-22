"""Bollinger reversal candles in a quiet trend, 1-hour bars: from flat, a green candle after a red one at or under the lower band (now or last bar), above the EMA 200 and EMA 100, with the RSI 40-60 and
the ADX under 20, goes long; the mirror at the upper band goes short; a reversal candle at the other band, an RSI under 30 or over 70, or the close beyond the swing stop closes.
Port of FMZ strategy #442367 "玻尔班带RSIADXATR反转交易策略Reversal-Trading-Strategy-with-Bollinger-Bands-RSI-ADX-and-ATR" (BB + EMA + RSI + ADX + ATR Reversal).

FMZ source id: 442367

Source
    https://www.fmz.com/strategy/442367 (PineScript v4, FMZ last modified 2024-02-21 14:13:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-249), EMA 200 / 100; BB 20 / 2; RSI 14 (entry 40-60, exit 30 / 70); ATR 14, structure stop on, look-back 7, x 1; ADX 14 / 14 (max 20); dates 2000-2099
    CrossLongEntry = (close <= lower or close[1] <= lower[1]) and close > open and close[1] < open[1] and close > ema200 and close > ema100 and flat and 40 < rsi < 60 and adx < 20;  short mirrored
    CrossLongExit = ((close >= upper or close[1] >= upper[1]) and close < open and close[1] > open[1] and long) or rsi < 30 or rsi > 70;  StopLong = lowest(low, 7) - atr(14) set on the entry signal
    close Long when CrossLongExit or close < StopLong;  close Short when CrossShortExit or close > StopShort

Interpretation choices (Pine rules in SURVEY_README.md)
    * and binds tighter than or, so the RSI exits apply on their own. The stop is a bar-close test of the
      close against the swing level stored on the entry signal, sent at the next open (no broker stop).
      Entries need a flat position: opposite entries cannot occur (entries only from flat). A close acts
      only on the held position. Pine's stdev is the population deviation. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band reversal candles with trend, RSI and ADX filters; close-tested swing stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442367_bb_reversal_candle_quiet_trend_swing_stop"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "adx_max": [20.0, 25.0],
}
DEFAULT_PARAMS = {"length": 20, "adx_max": 20.0, "mult": 2.0, "ema1": 200, "ema2": 100, "rsi_len": 14,
                  "rsi_max_entry": 60, "rsi_min_entry": 40, "rsi_max_exit": 70, "rsi_min_exit": 30,
                  "atr_len": 14, "atr_lookback": 7, "atr_mult": 1.0, "adx_len": 14, "di_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _adx(b, di_len, adx_len):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, di_len)
    plus = _fixnan(100 * _rma(pdm, di_len) / trr)
    minus = _fixnan(100 * _rma(mdm, di_len) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_len"]))
    adx = _adx(bars_df, int(p["di_len"]), int(p["adx_len"]))
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    lb = int(p["atr_lookback"])
    stop_l = (lo.rolling(lb).min() - atr).to_numpy()
    stop_s = (h.rolling(lb).max() + atr).to_numpy()
    green, red = c > o, c < o
    at_lo = (c <= dn) | (c.shift(1) <= dn.shift(1))
    at_up = (c >= up) | (c.shift(1) >= up.shift(1))
    calm = (r > float(p["rsi_min_entry"])) & (r < float(p["rsi_max_entry"])) & (adx < float(p["adx_max"]))
    el = (at_lo & green & red.shift(1, fill_value=False) & (c > e1) & (c > e2) & calm).to_numpy()
    es = (at_up & red & green.shift(1, fill_value=False) & (c < e1) & (c < e2) & calm).to_numpy()
    rx = ((r < float(p["rsi_min_exit"])) | (r > float(p["rsi_max_exit"]))).to_numpy()
    xl_band = (at_up & red & green.shift(1, fill_value=False)).to_numpy()
    xs_band = (at_lo & green & red.shift(1, fill_value=False)).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    sl_l = sl_s = 0.0
    for i in range(m):
        new = held
        if el[i] and held == 0:
            sl_l = stop_l[i]
        if es[i] and held == 0:
            sl_s = stop_s[i]
        if el[i] and held == 0:
            new = 1
        if held == 1 and new == 1 and ((xl_band[i] or rx[i]) or cv[i] < sl_l):
            new = 0
        if es[i] and held == 0 and new == 0:
            new = -1
        if held == -1 and new == -1 and ((xs_band[i] or rx[i]) or cv[i] > sl_s):
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
