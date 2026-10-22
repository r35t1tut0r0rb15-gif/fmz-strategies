"""Closes beyond the previous 20 bars' high / low by 1.5 ATR 14, on the EMA 50 side with RSI 14 beyond 50, 10-minute bars: the upside break goes long, the downside break goes short, each with a 1 ATR stop and a 2 ATR target around the fill; reversing.
Port of FMZ strategy #482848 "Volatility Momentum Breakout Strategy with Trend and Momentum Filters" (Volatility Momentum Breakout Strategy).

FMZ source id: 482848

Source
    https://www.fmz.com/strategy/482848 (PineScript v5, FMZ last modified 2025-02-20 15:13:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-200), ATR 14; breakout 1.5 ATR over the 20-bar high / low excluding the bar; EMA 50; RSI 14 / 50 / 50; stop 1 ATR, RR 2; 5 % of equity, capital 10000, commission 0.1 %, slippage 1
    close > highest(high[1], 20) + 1.5 atr and close > ema50 and rsi > 50 -> entry Long;  close < lowest(low[1], 20) - 1.5 atr and close < ema50 and rsi < 50 -> entry Short
    position long -> exit(stop = entry - atr, limit = entry + 2 atr), re-sent every bar with the current ATR;  short mirror;  entry prices reset only when flat

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent from the fill bar's close around the average price with that bar's ATR and
      re-sent every bar with the current ATR; the port fixes it from the fill at the signal bar's ATR
      (known at the fill open), active from the fill bar (as #440797), and marks the re-sent ATR distance
      trailing_stop_pending. The source resets its recorded entry prices only on a flat bar, so after a
      reversal back to an earlier side it keeps that side's old entry price; the port bases each bracket
      on its own fill (stated). The conditions repeat while they hold; a repeat entry on the side held
      adds nothing, the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver
      D4). The 5 % of equity size and the 2 % risk input (unused) are sizing; commission and slippage are
      costs (the house cost model applies). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, ATR-padded channel breaks with EMA / RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity stored, not ported (riskPercent unused).
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

NAME = "fmz_482848_prev20_channel_atr1_5_break_ema50_rsi50_atr_bracket_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_multiplier": [1.5, 1.0],
    "lookback": [20, 40],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.5, "lookback": 20, "atr_period": 14, "ema_period": 50, "rsi_period": 14,
                  "rsi_long": 50.0, "rsi_short": 50.0, "atr_stop_mult": 1.0, "risk_reward": 2.0}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_period"]))
    n = int(p["lookback"])
    hh, ll = h.shift(1).rolling(n).max(), lo.shift(1).rolling(n).min()
    k = float(p["atr_multiplier"])
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_period"]))
    le = (c > hh + k * atr) & (c > e) & (r > float(p["rsi_long"]))
    se = (c < ll - k * atr) & (c < e) & (r < float(p["rsi_short"]))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dist = float(p["atr_stop_mult"]) * _atr(bars_df, int(p["atr_period"]))
    f = dist.shift(1) / bars_df["open"]
    f = f.where(f > 0)
    return {"sl_stop": f, "tp_stop": f * float(p["risk_reward"])}


def portfolio_kwargs(**params):
    return {}
