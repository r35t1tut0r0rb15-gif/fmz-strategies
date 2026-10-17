"""Donchian 50 breakouts with the MACD side, 1-hour bars: a close above the previous 50-bar high with the MACD (12 / 26 / 9)
above its signal and the signal above the histogram goes long; the mirror below the previous 50-bar low goes short; a
4 ATR stop from the signal close; the MACD crossing back closes the trade. The stop re-set on every later signal is
not emitted.
Port of FMZ strategy #432185 "基于MACD的扩散通道趋势跟踪策略Trend-Following-Strategy-with-MACD-and-Donchian-Channel" (Trend Following with Donchian Channels and MACD).

FMZ source id: 432185

Source
    https://www.fmz.com/strategy/432185 (PineScript v5, FMZ last modified 2023-11-15 11:37:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 213-280), MACD 12 / 26 / 9 (EMA), Donchian 50 / 50 of the previous bars, ATR 14, stop 4 ATR, pyramiding 3
    close > highest(high[1], 50) and macd > signal and (macd and signal > hist) -> entry long, exit("exit sl", stop = close - 4 atr)
    crossover(signal, macd) and signal > macd and (macd and signal < hist) -> close long
    close < lowest(low[1], 50) and signal > macd and (macd and signal < hist) -> entry short, exit("exit sl", stop = close + 4 atr)
    crossover(macd, signal) and macd > signal and (macd and signal > hist) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "macd and signal > hist" reads the MACD value as a condition: true when it is non-zero (Pine's
      number-to-bool rule), so the term is (macd != 0) and (signal > hist), as written.
    * The channel excludes the current bar (high[1], low[1]). The stop is 4 ATR from the signal close:
      sl_atr x ATR / close of the signal bar, shifted one bar inside stops() and re-based on the fill.
      trail_offset = stoploss without trail_points arms no trail.
    * Every later signal in the trade's direction re-issues "exit sl" with a new level (the adds are
      pyramiding, criterion 4): a stop that moves after entry cannot be expressed by stops(): rule 2,
      mark trailing_stop_pending; the port keeps the first signal's level for the trade.
    * strategy.entry reverses (a later close of the other side does not undo it): REVERSAL INTENDED.
      The port's state machine follows the house stop on bars. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry (the re-set pending).
    2 generic: PASS, ATR stop, channel and MACD side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based amount and pyramiding 3 stored in original_sizing.txt.
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

NAME = "fmz_432185_donchian_macd_atr_stop"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "channel": [50, 20],
    "sl_atr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "channel": 50, "atr_len": 14, "sl_atr": 4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    hist = macd - sig
    nz = macd != 0
    n = int(p["channel"])
    h1 = h.shift(1).rolling(n).max()
    l1 = lo.shift(1).rolling(n).min()
    up_x = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn_x = (sig > macd) & (sig.shift(1) <= macd.shift(1))
    long_side = (macd > sig) & nz & (sig > hist)
    short_side = (sig > macd) & nz & (sig < hist)
    el = ((c > h1) & long_side).to_numpy()
    xl = (dn_x & short_side).to_numpy()
    es = ((c < l1) & short_side).to_numpy()
    xs = (up_x & long_side).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = float(p["sl_atr"])
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    sl_arr = np.full(m, np.nan)
    pos, e_i, sl = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house stop from the fill price
            ep = ov[e_i]
            if (pos == 1 and lv[i] <= ep * (1 - sl)) or (pos == -1 and hv[i] >= ep * (1 + sl)):
                pos = 0
        start = pos
        new = pos
        if el[i] and not np.isnan(af[i]):
            new = 1
        if xl[i] and start == 1 and new == 1:
            new = 0
        if es[i] and not np.isnan(af[i]):
            new = -1
        if xs[i] and start == -1 and new == -1:
            new = 0
        if new != 0 and new != start:
            e_i, sl = i + 1, af[i] * k
            sl_arr[i] = sl
            ent[i] = new
        pos = new
        tgt[i] = pos
    return tgt, ent, sl_arr


def _emit(tgt, ent, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
    lx = (prev == 1) & (tgt == 0)
    se = ent == -1
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent, _ = _run(bars_df, p)
    return _emit(tgt, ent, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr = _run(bars_df, p)
    return {"sl_stop": pd.Series(sl_arr, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
