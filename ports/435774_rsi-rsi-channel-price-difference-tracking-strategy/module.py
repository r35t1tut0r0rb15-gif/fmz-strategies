"""Hull-smoothed RSI band fades, 1-hour bars: the RSI of the close (Hull 3) crossing under 70 with the close under hl2 and the RSI of hl2 over 70
opens a long from flat; the RSI crossing back over 70, or the RSI of the low crossing under 55, closes it; the mirror at 30 / 45 opens and
closes shorts.
Port of FMZ strategy #435774 "RSI通道价差跟踪策略RSI-Channel-Price-Difference-Tracking-Strategy" (Hull MA of RSI Strategy).

FMZ source id: 435774

Source
    https://www.fmz.com/strategy/435774 (PineScript v4, FMZ last modified 2023-12-18 17:48:24).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 157-276), RSI 13, Hull 3; levels 70 / 30 and the channel 55 / 45
    rsi_x = hma(rsi(x, 13), 3) for x = close, high, low, hl2;  BuySignal = crossunder(rsi_c, 70) and close < hl2 and rsi_hl2 > 70 and status == "None";  CloseBuy = status[1] == "Long" and (crossover(rsi_c, 70) or crossunder(rsi_l, 55))
    SellSignal = crossover(rsi_c, 30) and close > hl2 and rsi_hl2 < 30 and status == "None";  CloseSell = status[1] == "Short" and (crossunder(rsi_c, 30) or crossover(rsi_h, 45));  status follows the signals

Interpretation choices (Pine rules in SURVEY_README.md)
    * The status variable is followed inside the script; the position follows it (entries only from
      "None"). hma(x, n) = wma(2 wma(x, n / 2) - wma(x, n), round(sqrt(n))): n / 2 is cut to a whole
      number of bars (1 for n = 3) and the root is rounded (2). The four orders are filled in the
      script's call order at the next open. Opposite entries cannot occur from a flat status; REVERSAL
      can arise only if both entry signals fire on one bar: the short (sent last) stands. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed RSI bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435774_hull_rsi_band_fade"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [13, 21],
    "hma_len": [3, 5],
}
DEFAULT_PARAMS = {"rsi_len": 13, "hma_len": 3, "upper": 55.0, "lower": 45.0, "ovb": 70.0, "ovs": 30.0}


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


def _rsi(x, n):
    ch = x.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())


def _wma(s, n):
    n = max(int(n), 1)
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def _hma(s, n):
    return _wma(2 * _wma(s, n // 2) - _wma(s, n), int(round(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    n, k = int(p["rsi_len"]), int(p["hma_len"])
    rc, rh, rl, rhl2 = (_hma(_rsi(x, n), k) for x in (c, h, lo, hl2))
    ovb, ovs, up, dn = float(p["ovb"]), float(p["ovs"]), float(p["upper"]), float(p["lower"])

    def xo(a, lv):
        return ((a > lv) & (a.shift(1) <= lv)).fillna(False).to_numpy()

    def xu(a, lv):
        return ((a < lv) & (a.shift(1) >= lv)).fillna(False).to_numpy()

    buy_sig = xu(rc, ovb) & (c < hl2).to_numpy() & (rhl2 > ovb).to_numpy()
    sell_sig = xo(rc, ovs) & (c > hl2).to_numpy() & (rhl2 < ovs).to_numpy()
    close_buy_c = xo(rc, ovb) | xu(rl, up)
    close_sell_c = xu(rc, ovs) | xo(rh, dn)
    m = len(buy_sig)
    held = np.zeros(m, dtype=np.int8)
    status = 0                               # 0 none, 1 long, -1 short (the value at the end of the last bar)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:       # fills at this bar's open, in the script's call order
            e_l, c_l, e_s, c_s = pend
            if e_l and pos <= 0:
                pos = 1
            if c_l and pos == 1:
                pos = 0
            if e_s and pos >= 0:
                pos = -1
            if c_s and pos == -1:
                pos = 0
        held[i] = pos
        buy = bool(buy_sig[i]) and status == 0
        sell = bool(sell_sig[i]) and status == 0
        close_buy = status == 1 and bool(close_buy_c[i])
        close_sell = status == -1 and bool(close_sell_c[i])
        new = status
        if buy:
            new = 1
        if sell:
            new = -1
        if close_buy or close_sell:
            new = 0
        status = new
        pend = (buy, close_buy, sell, close_sell)
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
