"""Slow Heiken-Ashi candle bodies in an EMA 100 trend, 15-minute bars: with the close over the EMA 100 and the smoothed candle body shrinking (and not flat) go long; under it and shrinking go short; the
close rules sit inside the entry blocks, so a position is closed only on a bar that also signals, two bars after an open crossing of the candle close.
Port of FMZ strategy #436228 "Slow Heiken Ashi Exponential Moving Average Trading Strategy" (NoScoobies Slow Heiken Ashi and EMA Strategy 2.2).

FMZ source id: 436228

Source
    https://www.fmz.com/strategy/436228 (PineScript v2, FMZ last modified 2023-12-22 13:18:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 143-203), SMA 6 of OHLC; Heiken-Ashi open = Kaufman average of the previous close; EMA 100
    vClose = (sma(open, 6) + sma(high, 6) + sma(low, 6) + sma(close, 6)) / 4;  vOpen = kama(vClose[1], 1) (fast 0.666, slow 0.0645);  size = |vOpen - vClose|
    long = close > ema100 and size < size[1] and vOpen != vClose;  short = close < ema100 and size < size[1] and vOpen != vClose;  close_long = long trend and crossunder(open, vClose);  _close = close_long[2] or close_short[2]
    if long: entry long, close long when _close;  if short: entry short, close short when _close

Interpretation choices (Pine rules in SURVEY_README.md)
    * kama with a one-bar length has an efficiency ratio of 1, so vOpen is an exponential average of the previous
      vClose with weight 0.666^2, seeded with the first value. The close calls are made only inside
      the matching entry block (a position is closed on a bar that also signals an entry of the same
      side, then the entry and the close both sit at the next open: flat). The orders are filled in the
      script's call order at the next open. REVERSAL INTENDED. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed candle bodies and an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436228_slow_heiken_ashi_ema_trend"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p": [6, 10],
    "exponential": [True, False],
}
DEFAULT_PARAMS = {"p": 6, "exponential": True, "fastend": 0.666, "slowend": 0.0645, "ma_len": 100}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["p"])
    v_close = (o.rolling(n).mean() + h.rolling(n).mean() + lo.rolling(n).mean() + c.rolling(n).mean()) / 4
    src = v_close.shift(1).to_numpy()
    smooth = (1.0 * (float(p["fastend"]) - float(p["slowend"])) + float(p["slowend"])) ** 2
    m = len(src)
    v_open = np.full(m, np.nan)
    for i in range(m):
        if np.isnan(src[i]):
            continue
        prev = v_open[i - 1] if i > 0 and not np.isnan(v_open[i - 1]) else src[i]
        v_open[i] = prev + smooth * (src[i] - prev)
    vo = pd.Series(v_open, index=c.index)
    size = (vo - v_close).abs()
    ma = c.ewm(span=int(p["ma_len"]), adjust=False).mean() if p["exponential"] else c.rolling(int(p["ma_len"])).mean()
    long_cond, short_cond = c > ma, c < ma
    shrink = size < size.shift(1)
    differ = vo != v_close
    long_ = (long_cond & shrink & differ).fillna(False)
    short_ = (short_cond & shrink & differ).fillna(False)
    cross_dn = (o < v_close) & (o.shift(1) >= v_close.shift(1))
    cross_up = (o > v_close) & (o.shift(1) <= v_close.shift(1))
    close_long = (long_cond & cross_dn).fillna(False)
    close_short = (short_cond & cross_up).fillna(False)
    _close = (close_long.shift(2, fill_value=False) | close_short.shift(2, fill_value=False)).to_numpy()
    lg, sh = long_.to_numpy(), short_.to_numpy()
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            eL, cL, eS, cS = pend
            if eL and pos <= 0:
                pos = 1
            if cL and pos == 1:
                pos = 0
            if eS and pos >= 0:
                pos = -1
            if cS and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(lg[i]), bool(lg[i] and _close[i]), bool(sh[i]), bool(sh[i] and _close[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
