"""NoNonsense Forex template, 15-minute bars: an Aroon (8) up-cross confirmed by PSAR, RSI 14 over 50 and a positive MACD
histogram, with the close inside the Kijun 20 +- 1 ATR cave, goes long (mirror short), with the source's tiny price-unit
stop and target as ATR fractions.
Port of FMZ strategy #430744 "双向ATR波浪交易策略Dual-ATR-Channel-Trend-Following-Strategy" (NoNonsense Forex).

FMZ source id: 430744

Source
    https://www.fmz.com/strategy/430744 (PineScript v4, FMZ last modified 2023-11-01 11:40:07).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 140-284), Kijun 20, ATR 14, Aroon 8, MACD 13 / 26 / 9, RSI 14, PSAR 0.03 / 0.018 / 0.11, SL 0.5 / TP 0.005 (price units)
    c1upper = 100 (highestbars(high, 9) + 8) / 8; c1lower = 100 (lowestbars(low, 9) + 8) / 8
    GoLong = crossover(c1upper, c1lower) and close > psar and rsi > 50 and macd_hist > 0 and close <= kijun + atr
    GoShort = crossunder(c1upper, c1lower) and close < psar and rsi < 50 and macd_hist < 0 and close >= kijun - atr
    exit(loss = 0.5 / mintick, profit = 0.005 / mintick) for each side (price distances 0.5 and 0.005)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop and target are price units (0.5 and 0.005 of the quote currency); they
      become sl_atr / tp_atr x the strategy's own ATR (Wilder 14) of the signal bar, as fractions of
      its close (0.5 USD is about 0.008 ATR and 0.005 USD about 0.0001 ATR on 15-minute BTC), fixed
      at entry. As written the target is hit almost at once.
    * highestbars / lowestbars count back from the current bar (0 = this bar); a tie takes the most
      recent bar. PSAR as TradingView documents ta.sar. The exit-on-opposite-cross option is off.
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit stop / target -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out order size stored; the exits quoted in original_sizing.txt.
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

NAME = "fmz_430744_nononsense_forex_aroon"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.008, 1.0],
    "tp_atr": [0.0001, 1.0],
}
DEFAULT_PARAMS = {"base_len": 20, "atr_len": 14, "aroon": 8, "fast": 13, "slow": 26, "signal": 9, "rsi_len": 14,
                  "ps_start": 0.03, "ps_inc": 0.018, "ps_max": 0.11, "sl_atr": 0.008, "tp_atr": 0.0001}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def _bars_since_extreme(x, n, highest):
    """highestbars / lowestbars(x, n) as a non-positive offset; a tie takes the most recent bar."""
    def f(a):
        r = a[::-1]
        k = int(np.argmax(r)) if highest else int(np.argmin(r))
        return -float(k)
    return x.rolling(n).apply(f, raw=True)


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["base_len"])
    base = (lo.rolling(n).min() + h.rolling(n).max()) / 2
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    too_high, too_low = c > base + atr, c < base - atr
    a = int(p["aroon"])
    up_ = 100 * (_bars_since_extreme(h, a + 1, True) + a) / a
    dn_ = 100 * (_bars_since_extreme(lo, a + 1, False) + a) / a
    xo = (up_ > dn_) & (up_.shift(1) <= dn_.shift(1))
    xu = (up_ < dn_) & (up_.shift(1) >= dn_.shift(1))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    ps = _sar_pine(bars_df, float(p["ps_start"]), float(p["ps_inc"]), float(p["ps_max"]))
    go_long = (xo & (c > ps) & (r > 50) & (hist > 0) & ~too_high).astype(bool)
    go_short = (xu & (c < ps) & (r < 50) & (hist < 0) & ~too_low).astype(bool)
    return go_long, go_short, atr / c


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    go_long, go_short, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return go_long, false, go_short, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, atr_frac = _signals(bars_df, p)
    return {"sl_stop": (atr_frac * float(p["sl_atr"])).shift(1), "tp_stop": (atr_frac * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
