"""Closes crossing out of the Bollinger band (20, 2) with RSI 14 between 40 and 60 and an SMA-smoothed ADX above 25,
with a 1.5 ATR stop and a 0.5 ATR trailing stop active from the entry, hourly bars.
Port of FMZ strategy #482824 "高级布林带指标组合动态趋势突破交易策略-Advanced-Bollinger-Bands-Multi-Indicator-Dynamic-Trend-Breakout-Trading-Strategy" (Optimized Bollinger Bands Breakout Strategy).

FMZ source id: 482824

Source
    https://www.fmz.com/strategy/482824 (PineScript v5, FMZ last modified 2025-02-20 14:52:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 120-164), BB 20 / 2, DMI / ADX 14 (SMA smoothing), RSI 14, ATR 14,
stop 1.5 ATR, trail 1 ATR / offset 0.5 ATR
    crossover(close, upper) and 40 < rsi < 60 and adx > 25 -> entry long with exit(stop = close - 1.5 ATR,
    trail_price = close - 1 ATR, trail_offset = 0.5 ATR) (short mirrored at the lower band)

Interpretation choices (Pine rules in SURVEY_README.md)
    * DI+ / DI- = SMA 14 of the directional moves / ATR 14 x 100, ADX = SMA 14 of DX (as written, not Wilder's).
    * The stop is placed with the entry: 1.5 ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill (house rule).
    * trail_price sits 1 ATR on the losing side of the close, so the trail is active from the entry; the trail_offset
      is a price distance passed to a tick argument and is read as a price distance (as #427592): the house trail
      {"type": "volatility", "atr_n": 14, "k": 0.5, "anchor": "high_low"} (the house ATR moves with each bar where
      Pine fixes the signal bar's ATR; as #428795). Mark trailing_stop.
    * Every bar in the condition is an entry signal (same-side ignored while held). Entries reverse (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop and trail set at entry.
    2 generic: PASS, Bollinger bands, RSI, a DMI / ADX and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity; the stop and trail via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482824_bb_break_rsi_mid_adx_atr_stop_trail"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "trail_k": [0.5, 1.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "dmi_len": 14, "adx_len": 14, "adx_min": 25.0, "rsi_len": 14,
                  "atr_len": 14, "sl_mult": 1.5, "trail_k": 0.5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    up_move, down_move = h - h.shift(1), lo.shift(1) - lo
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    k = int(p["dmi_len"])
    atr_d = _atr(bars_df, k)
    plus_di = plus_dm.rolling(k).mean() / atr_d * 100
    minus_di = minus_dm.rolling(k).mean() / atr_d * 100
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx = dx.rolling(int(p["adx_len"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    mid_rsi = (rsi > 40) & (rsi < 60) & (adx > p["adx_min"])
    long_e = ((c > upper) & (c.shift(1) <= upper.shift(1)) & mid_rsi).astype(bool)
    short_e = ((c < lower) & (c.shift(1) >= lower.shift(1)) & mid_rsi).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl,
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
