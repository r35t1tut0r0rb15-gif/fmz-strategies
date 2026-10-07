"""Moon Launch alerts template: EMA10 slope, MACD-histogram slope and an EMA +- ATR envelope feed a
state machine whose trade line is +1000 / -1000 / 0; a move onto +1000 goes long, onto -1000 goes
short (always in; the 0 "exit" line only raises an alert).
Port of FMZ strategy #362671 "ML Alerts Template [indicator]".

Source
    https://www.fmz.com/strategy/362671 (PineScript v5, FMZ last modified 2022-05-12 18:45:45).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 76-245), EMA 10, ATR 12, MACD 12/26/9 (SMA signal)
    tradeups   = ema10 rising and low > ema12 - atr and hist rising
    tradeexits = ema10 falling and not tradeups
    tradedowns = ((ema10 falling and hist falling) or (high > ema12 + atr and close < ema12 + atr
                 and close < open and hist falling)) and not tradeups
    exitshort  = low < ema12 - atr and close > open and ema10 rising and hist rising
    in-a-short / in-a-long / in-an-exit / in-a-short-exit latches (lines 175-202), filtered
    colours (lines 207-210), prev5 = 1000 / -1000 / 0 (line 213)
    GoLong = prev5 > 0 and prev5[1] < 900 -> entry long; else GoShort = prev5 < 0 and
    prev5[1] > -900 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * prev5 is re-declared 0 on every bar, so its fallback prev5[0] is 0 (not the previous
      value); the latches use [1] and so carry state. Ternary/and/or precedence as Pine.
    * "Trade Shorts" and "Trade Exits" default to true. GoExit only feeds an alert: no order.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362671_moon_launch_state_machine"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [10, 20],
    "atr_len": [12, 24],
}
DEFAULT_PARAMS = {"ema1": 10, "atr_len": 12, "fast": 12, "slow": 26, "signal": 9}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _latch(on, off):
    """state = 1 if on else -1 if off else state[1]; returns state[1] == 1."""
    st = np.zeros(len(on))
    for i in range(len(on)):
        st[i] = 1.0 if on[i] else (-1.0 if off[i] else (st[i - 1] if i else 0.0))
    prev = np.concatenate([[0.0], st[:-1]])
    return prev == 1.0


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n_atr = int(p["atr_len"])
    e10 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    atr = _atr_pine(bars_df, n_atr)
    ema = c.ewm(span=n_atr, adjust=False).mean()
    up_b, dn_b = ema + atr, ema - atr
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["signal"])).mean()
    e_up, e_dn = (e10 > e10.shift(1)).to_numpy(), (e10 < e10.shift(1)).to_numpy()
    h_up, h_dn = (hist > hist.shift(1)).to_numpy(), (hist < hist.shift(1)).to_numpy()

    ups = e_up & (l > dn_b).to_numpy() & h_up
    exits = e_dn & ~ups
    downs = ((e_dn & h_dn) | ((h > up_b) & (c < up_b) & (c < o)).to_numpy() & h_dn) & ~ups
    exitshort = ((l < dn_b) & (c > o)).to_numpy() & e_up & h_up

    inashort2 = _latch(downs & ~ups, ups)
    inalong2 = _latch(ups & ~(downs | exits), downs)
    inaexit2 = _latch(exits & ~downs & ~ups, downs | ups)
    inasexit2 = _latch(exitshort & (inashort2 | downs) & ~ups, downs | ups)

    down_f = (downs & ~ups) | (downs & ~exits)
    up_f = ups | ((ups | inalong2) & ~(exits | downs | (inaexit2 & ~ups)))
    exit_f = exits & ~(down_f | ups)

    c1 = (up_f & ~(downs | exits)) | ups
    c2 = downs | (~(inashort2 & (exitshort | inasexit2)) & (inashort2 | down_f))
    # the third branch (-> 0) and the fallback prev5[0] (the bar's own 0) both give 0
    prev5 = np.where(c1, 1000.0, np.where(c2, -1000.0, 0.0))
    p1 = np.concatenate([[np.nan], prev5[:-1]])
    go_long = (prev5 > 0) & (p1 < 900)
    go_short = (prev5 < 0) & (p1 > -900)
    return _always_in(go_long, go_short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
