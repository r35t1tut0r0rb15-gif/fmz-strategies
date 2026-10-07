"""MACD histogram turn-up entry above the zero line (long only), with bearish-candle,
histogram and deep-loss exits.
Port of FMZ strategy #194224 "MACD低买高卖自动跟单滑动止损" (MACD buy-low sell-high with stop).

Source
    https://www.fmz.com/strategy/194224 (JavaScript, author "John。", FMZ last modified
    2020-04-20 11:54:46). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 148-197), ac1 0.005, bc1 -1e-6, TrailingStop 0.5
    dif, dea, his = TA.MACD(records, 12, 26, 9)
    flat: dif[-1] > 0 && his[-1] > ac1 && his[-2] < bc1 -> buy (all balance)
    long, any of:
      (a) records[-2].Time > timeAtBuy && bar[-1] and bar[-2] close < open - 0.5
          && close[-1] < close[-2] - 0.5
      (b) records[-2].Time > timeAtBuy && buyPrice > close[-1] && close[-1] < open[-1] - 0.5
      (c) (buyPrice < ticker.Last || dif[-1] < 0) && his[-1] <= 0
      (d) buyPrice > ticker.Last && (buyPrice - ticker.Last)/buyPrice > TrailingStop
    -> sell all

Interpretation choices
    * The bot polls the forming bar every 30 s; the port evaluates on completed bar t
      (records[-1] and ticker.Last -> bar t, records[-2] -> t-1). timeAtBuy is the signal bar
      t_b, so (a)/(b) apply from bar t_b+2. buyPrice is the fill, i.e. the open of bar t_b+1.
    * Criterion 2: the 0.5 price-unit candle margins become `body_atr` x ATR(14) on bar t; the
      histogram threshold ac1 (price units) becomes `hist_atr` x ATR(14); bc1 (-1e-6) is read as
      "below zero". "TrailingStop" is a fixed 50 % loss from the buy price (not a trailing stop),
      a close condition -> exit signal, re-expressed as `stop_atr` x ATR(14) of the signal bar.
    * MACD EMAs as FMZ's TA (pandas ewm adjust=False); histogram = dif - dea.
    * Long only (spot); shorts are never emitted, so opposite entries cannot occur.
    * No bar size in the source (GetRecords() default, no backtest header):
      FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_194224_macd_hist_turn_long"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hist_atr": [0.0, 0.05, 0.1],
    "body_atr": [0.1, 0.25, 0.5],
    "stop_atr": [5.0, 10.0, 20.0],
}
DEFAULT_PARAMS = {"hist_atr": 0.05, "body_atr": 0.25, "stop_atr": 10.0, "fast": 12, "slow": 26,
                  "signal": 9, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    dif = close.ewm(span=int(p["fast"]), adjust=False).mean() - close.ewm(span=int(p["slow"]), adjust=False).mean()
    his = (dif - dif.ewm(span=int(p["signal"]), adjust=False).mean()).to_numpy()
    dif = dif.to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    o = bars_df["open"].to_numpy(dtype=float)
    c = close.to_numpy(dtype=float)
    warm = np.arange(len(c)) >= int(p["slow"]) + int(p["signal"])   # the bot needs 45 records

    m = len(c)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state, tb, buy_price, stop_dist = 0, -1, np.nan, np.nan   # 0 flat, 1 entry pending, 2 long
    for i in range(m):
        if state == 1:
            state, buy_price = 2, o[i]            # filled at this bar's open
        if state == 0:
            if (warm[i] and not np.isnan(atr[i]) and dif[i] > 0
                    and his[i] > p["hist_atr"] * atr[i] and his[i - 1] < 0):
                entries[i], state, tb, stop_dist = True, 1, i, p["stop_atr"] * atr[i]
            continue
        b = p["body_atr"] * atr[i]
        aged = i >= tb + 2
        ex_a = aged and c[i] < o[i] - b and c[i - 1] < o[i - 1] - b and c[i] < c[i - 1] - b
        ex_b = aged and buy_price > c[i] and c[i] < o[i] - b
        ex_c = (buy_price < c[i] or dif[i] < 0) and his[i] <= 0
        ex_d = c[i] < buy_price - stop_dist
        if ex_a or ex_b or ex_c or ex_d:
            exits[i], state = True, 0

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
