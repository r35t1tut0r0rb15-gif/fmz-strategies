"""RSI of the ultimate oscillator, short only, 30-minute bars: with the alligator lines (SMMA 10 / 20 / 50 of hl2) falling in
order and the close under the SMMA 20, the RSI 5 of the ultimate oscillator (5 / 10 / 15) crossing under 60 goes short;
its crossing above 75 covers. The one-third partial cover is sizing, not ported.
Port of FMZ strategy #432111 "海龟交易RSI指标短线策略RSI-Oscillator-Turtle-Trading-Short-term-Strategy" (RSI of Ultimate Oscillator [SHORT Selling] Strategy).

FMZ source id: 432111

Source
    https://www.fmz.com/strategy/432111 (PineScript v4, FMZ last modified 2023-11-14 15:59:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 193-278), UO 5 / 10 / 15, RSI 5, sell 60, cover 75; risk 10 %, stop 3 % used for the quantity only
    uo = 100 x (4 avg(5) + 2 avg(10) + avg(15)) / 7, avg(n) = sum(close - min(low, close[1]), n) / sum(max(high, close[1]) - min(low, close[1]), n)
    smma10 <= smma20 and smma20 < smma50 and close < smma20 and crossunder(rsi(uo, 5), 60) -> entry short
    crossover(rsi(uo, 5), 75) -> close all;  close < avg price and crossover(rsiUO, 30) -> close 1/3 (sizing)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Short only (long = false); pyramiding 1, so a repeated short signal while short is ignored.
      Opposite entries cannot occur.
    * The "Stop Loss" input (3 %) only sizes the order (qty1 = risk / stop distance); it places no
      exit order. The one-third partial cover (qty = position / 3) changes the position size only:
      criterion 4, quoted in original_sizing.txt, not ported.
    * SMMA = Wilder smoothing seeded with an SMA (as the source's smma()); RSI = Wilder. Rolling sums
      include the current bar. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and moving-average order.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 20 % of equity, the risk-based quantity and the partial cover stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432111_rsi_of_uo_short"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [5, 9],
    "sell_line": [60, 50],
}
DEFAULT_PARAMS = {"l1": 5, "l2": 10, "l3": 15, "rsi_len": 5, "sell_line": 60, "cover_line": 75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smma(x, n):
    """Wilder smoothing seeded with the SMA of the first n values (the source's smma())."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    sma = x.rolling(n).mean().to_numpy(dtype=float)
    prev = np.nan
    for i in range(len(v)):
        if np.isnan(prev):
            prev = sma[i]
        elif not np.isnan(v[i]):
            prev = (prev * (n - 1) + v[i]) / n
        out[i] = prev
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    hi_ = pd.concat([h, c1], axis=1).max(axis=1)
    lo_ = pd.concat([lo, c1], axis=1).min(axis=1)
    bp, tr = c - lo_, hi_ - lo_
    avg = lambda n: bp.rolling(n).sum() / tr.rolling(n).sum()  # noqa: E731
    uo = 100 * (4 * avg(int(p["l1"])) + 2 * avg(int(p["l2"])) + avg(int(p["l3"]))) / 7
    r = _rsi(uo, int(p["rsi_len"]))
    hl2 = (h + lo) / 2
    s1, s2, s3 = _smma(hl2, 10), _smma(hl2, 20), _smma(hl2, 50)
    sl_, cv = float(p["sell_line"]), float(p["cover_line"])
    se = ((s1 <= s2) & (s2 < s3) & (c < s2) & (r < sl_) & (r.shift(1) >= sl_)).astype(bool)
    sx = ((r > cv) & (r.shift(1) <= cv)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
