"""3-minute bars: an EMA 5 above EMA 21 trend with RSI 14 under 45 and ATR 14 above 0.8 x its 14-bar average goes long; the mirror (RSI over 55) goes short; the opposite signal reverses.
Port of FMZ strategy #475601 "多重指标波动率交易RSI-EMA-ATR策略-Multi-Indicator-Volatility-Trading-RSI-EMA-ATR-Strategy" (Scalp Master BTCUSDT Strategy).

FMZ source id: 475601

Source
    https://www.fmz.com/strategy/475601 (PineScript v5, FMZ last modified 2024-12-20 14:47:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-175), RSI 14, 45 / 55; EMA 5 / 21; ATR 14 vs 0.8 x its SMA 14; volume filter off by default
    long_signal = trend_up and rsi < 45 and atr > sma(atr, 14) x 0.8 -> close Short, entry Long;  short_signal mirrored (rsi > 55) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume filter input defaults to false, so volume is not used (held for volume, not used). The
      close of the other side before each entry is what the entry's reversal already does. The entries
      are states; an entry while in that position adds nothing. REVERSAL INTENDED. Capital and commission
      are sizing and costs. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI pullbacks in an EMA trend with an ATR activity filter.
    3 crypto-exchange-only: no (exchange pair in the header only (BTCUSDT named in the title)).
    4 signals only: capital and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475601_ema5_21_rsi_pullback_atr_filter_3m_reversal"
FAMILY = "rsi_pullback"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_lo": [45.0, 40.0],
    "atr_mult": [0.8, 1.0],
}
DEFAULT_PARAMS = {"rsi_lo": 45.0, "atr_mult": 0.8}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    active = atr > atr.rolling(14).mean() * float(p["atr_mult"])
    f, s = c.ewm(span=5, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    lo_r = float(p["rsi_lo"])
    buy = (f > s) & (r < lo_r) & active
    sell = (f < s) & (r > 100 - lo_r) & active
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
