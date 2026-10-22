"""MACD 12 / 26 / 9 crossings confirmed by the Ichimoku lines, 1-hour bars: a MACD cross up with the close over both (undisplaced) spans and the Tenkan over the Kijun goes long; the mirror, with the Tenkan 26 bars back under the spans, goes short; a 5-tick stop and 10-tick target (0.0033 / 0.0067 ATR); reversing.
Port of FMZ strategy #451703 "动态MACD和一目均衡图交易策略-Dynamic-MACD-and-Ichimoku-Cloud-Trading-Strategy" (MACD and Ichimoku Cloud Strategy).

FMZ source id: 451703

Source
    https://www.fmz.com/strategy/451703 (PineScript v5, FMZ last modified 2024-05-17 10:45:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-143), MACD 12 / 26 / 9; Tenkan 9, Kijun 26, Senkou B 52, displacement 26 (plots only); exit loss 5 / profit 10 ticks
    crossover(macd, signal) and close > spanA and close > spanB and tenkan > kijun -> entry Buy
    crossunder(macd, signal) and close < spanA and close < spanB and tenkan < kijun and tenkan[26] < min(spanA, spanB) -> entry Sell
    exit(Buy / Sell, loss = 5, profit = 10)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are compared at the current bar (the 26-bar displacement only moves the plots). The
      exit's loss / profit are tick distances from the entry: 5 and 10 ticks are 0.5 and 1.0 at the
      0.1 tick, ported as ATR multiples at the 1-hour reading (~150): 0.0033 and 0.0067 ATR 14, read
      from the bar before the fill. The two entries cannot meet on one bar. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, MACD crossings with Ichimoku confirmation.
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

NAME = "fmz_451703_macd_cross_ichimoku_confirm_tick_bracket_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.0033, 1.0],
    "tp_atr": [0.0067, 2.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.0033, "tp_atr": 0.0067, "atr_len": 14,
                  "tenkan": 9, "kijun": 26, "senkou": 52, "disp": 26}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    tenkan, kijun = mid(p["tenkan"]), mid(p["kijun"])
    span_a, span_b = (tenkan + kijun) / 2, mid(p["senkou"])
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    le = up & (c > span_a) & (c > span_b) & (tenkan > kijun)
    se = (dn & (c < span_a) & (c < span_b) & (tenkan < kijun)
          & (tenkan.shift(int(p["disp"])) < np.minimum(span_a, span_b)))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
