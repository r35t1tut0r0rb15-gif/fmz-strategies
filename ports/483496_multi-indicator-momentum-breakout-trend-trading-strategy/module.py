"""Williams %R leaving oversold (overbought) on the same bar as a MACD cross, on the EMA 55 side, with a tick
bracket read as percentages, 1-minute bars: %R(14) crossing above -80 with MACD crossing above its signal and the close
above EMA 55 goes long; %R crossing below -20 with MACD crossing below and the close below EMA 55 goes short.
Port of FMZ strategy #483496 "多重指标动量突破趋势交易策略-Multi-Indicator-Momentum-Breakout-Trend-Trading-Strategy" (Williams %R & MACD Swing Strategy).

FMZ source id: 483496

Source
    https://www.fmz.com/strategy/483496 (PineScript v5, FMZ last modified 2025-02-24 09:18:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-139), %R 14 (-20 / -80), MACD 12 / 26 / 9, EMA 55, SL 2 %, RR 1.5
    long = crossover(wpr, -80) and crossover(macd, signal) and close > ema55 (short mirrored)
    exit(loss = avg_price x 0.98, profit = avg_price x 1.03) for the long; (loss = avg_price x 1.02,
    profit = avg_price x 0.97) for the short, on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit's loss / profit are TICKS, and the author passes PRICES: the distances are price x 0.98 (1.03)
      ticks. On the author's market (Binance SOL_USDT, mintick 0.01) that is 0.98 % stop / 1.03 % target for a long and
      1.02 % stop / 0.97 % target for a short, of the fill (as #427729: the tick reading ported as written). Picked by
      the signal's side, shifted one bar inside stops(); bracket_mult scales both (GRID).
    * The exits use strategy.position_avg_price on every bar: fixed from the fill (no moving level).
    * ta.wpr = 100 x (close - highest high 14) / (highest high 14 - lowest low 14).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed bracket from the fill.
    2 generic: PASS, %R, MACD, an EMA and distances relative to price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483496_wpr_macd_cross_ema55_tick_bracket"
FAMILY = "oscillator_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bracket_mult": [1.0, 2.0],
    "ema_length": [55, 100],
}
DEFAULT_PARAMS = {"wpr_len": 14, "overbought": -20.0, "oversold": -80.0, "fast": 12, "slow": 26, "signal": 9,
                  "ema_length": 55, "bracket_mult": 1.0,
                  "long_sl": 0.0098, "long_tp": 0.0103, "short_sl": 0.0102, "short_tp": 0.0097}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["wpr_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wpr = 100 * (c - hh) / (hh - ll)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    os_, ob = p["oversold"], p["overbought"]
    w_up = (wpr > os_) & (wpr.shift(1) <= os_)
    w_dn = (wpr < ob) & (wpr.shift(1) >= ob)
    m_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    m_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    long_e = (w_up & m_up & (c > ema)).astype(bool)
    short_e = (w_dn & m_dn & (c < ema)).astype(bool)
    return long_e, short_e


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _ = _signals(bars_df, p)
    k = p["bracket_mult"]
    sl = pd.Series(np.where(long_e, p["long_sl"], p["short_sl"]) * k, index=bars_df.index)
    tp = pd.Series(np.where(long_e, p["long_tp"], p["short_tp"]) * k, index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
