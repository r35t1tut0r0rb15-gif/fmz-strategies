"""Hourly bars: Tenkan 10 over Kijun 30, the close above its value 25 bars back and above the cloud drawn 26 bars back, a positive MACD histogram (SMA 12 / 26 of hl2, EMA 9 signal), a Chaikin money flow 10 over 0.1 and a TSI 20 / 20 above 0 all together go long; the mirror set goes short; reversing.
Port of FMZ strategy #432909 "Kairou Strategy" (Ichimoku with MACD/ CMF/ TSI).

FMZ source id: 432909

Source
    https://www.fmz.com/strategy/432909 (PineScript v4, FMZ last modified 2023-11-22 16:28:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-252), Tenkan 10, Kijun 30, Senkou B 52, offsets 26; MACD SMA 12 / 26 of hl2, signal EMA 9; CMF 10, +-0.1; TSI 20 / 20; long and short entries on
    bullish = tenkan > kijun and mom(close, 25) > 0 and close > max(senkouA[25], senkouB[25]) and hist > 0 and mf > 0.1 and tsi > 0;  bearish mirror
    bullish -> entry Long;  bearish -> entry Short;  close Long when bearish and not short_entry (never, short_entry on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With both entry switches on, the strategy.close conditions ("... and not short_entry") are always
      false, so a position ends only at the opposite entry. The MACD uses SMAs for the oscillator
      (Simple MA(Oscillator) on) and an EMA for the signal. middle(len) uses highest(high) / lowest(low).
      The money flow is a ratio of volume sums. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku trend with MACD, money-flow and TSI agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432909 (3 members, best partner #433407, Jaccard 0.851); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow sum(ad, 10) / sum(volume, 10); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432909_ichimoku_macd_cmf_tsi_agreement_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ks_bars": [30, 26],
    "cmf_level": [0.1, 0.05],
}
DEFAULT_PARAMS = {"ts_bars": 10, "ks_bars": 30, "ssb_bars": 52, "cs_offset": 26, "ss_offset": 26,
                  "cmf_len": 10, "cmf_level": 0.1, "tsi_long": 20, "tsi_short": 20}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))

    def mid(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    tenkan, kijun, sb = mid(int(p["ts_bars"])), mid(int(p["ks_bars"])), mid(int(p["ssb_bars"]))
    sa = (tenkan + kijun) / 2
    k = int(p["ss_offset"]) - 1
    ss = pd.concat([sa.shift(k), sb.shift(k)], axis=1)
    ss_high, ss_low = ss.max(axis=1, skipna=False), ss.min(axis=1, skipna=False)
    mom = c - c.shift(int(p["cs_offset"]) - 1)
    hl2 = (h + lo) / 2
    macd = hl2.rolling(12).mean() - hl2.rolling(26).mean()
    hist = macd - _ema(macd, 9)
    ad = pd.Series(np.where(((c == h) & (c == lo)) | (h == lo), 0.0,
                            (2 * c - lo - h) / (h - lo).where(h != lo)), index=c.index) * v
    n = int(p["cmf_len"])
    sv = v.rolling(n).sum()
    mf = ad.rolling(n).sum() / sv.where(sv != 0)
    pc = c.diff()
    ds = _ema(_ema(pc, int(p["tsi_long"])), int(p["tsi_short"]))
    da = _ema(_ema(pc.abs(), int(p["tsi_long"])), int(p["tsi_short"]))
    tsi = 100 * ds / da.where(da != 0)
    lvl = float(p["cmf_level"])
    bull = (tenkan > kijun) & (mom > 0) & (c > ss_high) & (hist > 0) & (mf > lvl) & (tsi > 0)
    bear = (tenkan < kijun) & (mom < 0) & (c < ss_low) & (hist < 0) & (mf < -lvl) & (tsi < 0)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return bull, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
