"""Hourly bars: a MACD cross-up at least 1 % above its signal line (relative), above the SMA 50 with RSI 14 over 30 on above-average volume, goes long with a 1 % stop and 2 % target from its fill; the mirror goes short, but the short gets the long-side levels and so closes one bar after its fill; reversing.
Port of FMZ strategy #488295 "多指标MACD动量期权策略与风险控制百分比退出机制-Multi-Indicator-MACD-Momentum-Options-Strategy-with-Risk-Controlled-Percentage-Based-Exits" (MACD Options Trader - 30-Min (Simplified)).

FMZ source id: 488295

Source
    https://www.fmz.com/strategy/488295 (PineScript v5, FMZ last modified 2025-03-26 16:46:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-236), MACD 12 / 26 / 9; percentDiff = (macd - signal) / |signal| x 100 > 1; SMA 50; RSI 14 (70 / 30); volume SMA 20; SL 1 %, TP 2 % of position_avg_price (both sides)
    bullishMove = crossover(macd, signal) and percentDiff > 1 and close > sma50 and rsi > 30 and volume > sma(volume, 20) -> entry BUY Call;  bearishMove mirrored -> entry SELL Put
    every bar: exit("BUY Exit", "BUY Call", limit = avg x 1.02, stop = avg x 0.99);  exit("SELL Exit", "SELL Put", limit = avg x 1.02, stop = avg x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short's exit uses the long's levels: a buy limit above and a buy stop below the price, both
      met at once, so a short closes at the open after its fill bar (in the signals: a close sent on the
      fill bar; weird case). The long's bracket is re-sent from position_avg_price every bar from the
      fill bar's close, so it is fixed at the fill: ported as sl_stop 0.01 / tp_stop 0.02 for longs
      (stated approximation: the source acts from the bar after the fill, the house from the fill, as
      #429494). The title names 30 minutes and options; the header is 1 hour. REVERSAL INTENDED. No
      sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 1 % / 2 % bracket from the fill (longs), one-bar shorts.
    2 generic: PASS, sharp MACD crossings in the SMA 50 trend on volume.
    3 crypto-exchange-only: no (exchange pair in the header only (SPY / Tesla / Apple named in the comments)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488295_sharp_macd_cross_sma50_volume_bracket_1h_reversal"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sharp": [1.0, 5.0],
    "sl": [0.01, 0.02],
}
DEFAULT_PARAMS = {"sharp": 1.0, "sl": 0.01, "tp": 0.02}


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
    c, v = bars_df["close"], bars_df["volume"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    pdiff = (macd - sig) / sig.abs().where(sig != 0) * 100
    ma = c.rolling(50).mean()
    r = _rsi(c, 14)
    hv = v > v.rolling(20).mean()
    k = float(p["sharp"])
    buy = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (pdiff > k) & (c > ma) & (r > 30) & hv
    sell = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (pdiff < -k) & (c < ma) & (r < 70) & hv
    sx = sell.shift(1, fill_value=False) & ~buy & ~sell   # the short's long-side exit closes it after its fill bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), sx.astype(bool)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    lf = le.shift(1, fill_value=False)
    sl_f = pd.Series(float(p["sl"]), index=bars_df.index).where(lf)
    tp_f = pd.Series(float(p["tp"]), index=bars_df.index).where(lf)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
