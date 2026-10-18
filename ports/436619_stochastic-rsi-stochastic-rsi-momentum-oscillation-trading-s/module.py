"""Stochastic RSI crossing from oversold with a trend filter, 1-hour bars, long only: a K line crossing over D with D at or under 30.6, while the close is over the 60-bar EMA, goes long; an overbought death cross (D at or over 85.29)
closes it six bars later in an up-trend (at once in a down-trend); the long has a 10 % stop and an 8 % target. The shorts are switched off; the gamble sizing is sizing.
Port of FMZ strategy #436619 "动量震荡Stochastic-RSI交易策略Stochastic-RSI-Momentum-Oscillation-Trading-Strategy" (Momentum Strategy (V7.B.4)).

FMZ source id: 436619

Source
    https://www.fmz.com/strategy/436619 (PineScript v4, FMZ last modified 2023-12-26 12:11:21).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 169-354), stochastic RSI 12 / 12 / 3 / 6, levels 85.29 / 30.6, trend EMA 1 / 60, bars delay 6, stop 10 %, target 8 %
    k = ema(stoch(rsi(close, 12), 12), 3), d = ema(k, 6);  oversold = crossover(k, d) and d <= 30.6;  overbought = crossunder(k, d) and d >= 85.29;  uptrend = ema(close, 1) > ema(close, 60)
    open long (flat) = oversold and uptrend;  close long = (uptrend and barssince(overbought) == 6) or (not uptrend and overbought);  exit(stop = avg price x 0.9, limit = avg price x 1.08)
    the short side is gated by a switch that is off

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long stop and target are fixed fractions of the fill price (10 % and 8 %), so the stop module
      carries them as scalars. The gamble sizing (the order size grows after a loss) and the equity
      based quantity are sizing. The start-date input (2020) is a backtest window and is treated as
      open. The short side is off by default and is not ported. Long only; the entry is only sent when
      flat (an entry while long is ignored). Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: REVIEW, stochastic RSI crossing with a trend filter and a delayed exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the gamble sizing and the quantity formula stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436619_stoch_rsi_cross_trend_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.10, 0.05],
    "tp_pct": [0.08, 0.04],
}
DEFAULT_PARAMS = {"sl_pct": 0.10, "tp_pct": 0.08, "rsi_len": 12, "stoch_len": 12, "smooth_k": 3, "smooth_d": 6,
                  "overbought": 85.29, "oversold": 30.6, "ema_slow": 60, "delay": 6}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    s = int(p["stoch_len"])
    lo, hi = rsi.rolling(s).min(), rsi.rolling(s).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (rsi - lo) / (hi - lo).where(hi > lo)
    k = st.ewm(span=int(p["smooth_k"]), adjust=False).mean()
    d = k.ewm(span=int(p["smooth_d"]), adjust=False).mean()
    gold = (k > d) & (k.shift(1) <= d.shift(1))
    death = (k < d) & (k.shift(1) >= d.shift(1))
    oversold = (gold & (d <= float(p["oversold"]))).fillna(False)
    overbought = (death & (d >= float(p["overbought"]))).fillna(False).to_numpy()
    uptrend = (c > c.ewm(span=int(p["ema_slow"]), adjust=False).mean()).to_numpy()
    since = np.full(len(c), -1)                # bars since the last overbought cross (-1: none yet)
    cnt = -1
    for i in range(len(c)):
        cnt = 0 if overbought[i] else (cnt + 1 if cnt >= 0 else -1)
        since[i] = cnt
    delayed = since == int(p["delay"])
    exit_sig = (uptrend & delayed) | (~uptrend & overbought)
    open_long = oversold & pd.Series(uptrend, index=c.index)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return open_long.astype(bool), pd.Series(exit_sig, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
