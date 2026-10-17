"""EMA 50 / SMA 200 cross with a mapped volatility line, 1-minute bars: after a golden cross, a close above the SMA 200 with
the mapped line under 25 (close at or below the EMA 20 and the 2-bar deviation in the top half of its 504-bar range) goes
long once; after a death cross the mirror goes short; the source's point target and stop become ATR fractions.
Port of FMZ strategy #430998 "木星与土星动能MA交叉过滤策略Jupiter-and-Saturn-Momentum-MA-Crossover-Filtered-Strategy" (EMA Difference Mapping with Trades).

FMZ source id: 430998

Source
    https://www.fmz.com/strategy/430998 (PineScript v4, FMZ last modified 2023-11-03 16:13:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-237), EMA 20, stdev 2, lookback 504, EMA 50 / SMA 200, TP 1000 / SL 2500 points
    diff1 = diff2 = stdev(close, 2); mapped = close > ema20 ? 50 + 50 x norm : 50 - 50 x norm (norm over 504 bars)
    crossunder(ema50, sma200) -> waitingForSell (waitingForBuy off); crossover -> waitingForBuy (waitingForSell off)
    waitingForSell and close < sma200 and mapped > 75 -> entry short, exit(profit 1000, loss 2500); waitingForSell off
    waitingForBuy and close > sma200 and mapped < 25 -> entry long, same exit; waitingForBuy off

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bracket is 1000 / 2500 ticks (100 / 250 USD on BTC_USDT at mintick 0.1); it
      becomes tp_atr / sl_atr x the Wilder ATR 14 of the signal bar, as fractions of its close (about
      5 and 12.5 ATR on 1-minute BTC), fixed at entry.
    * The flags follow the source's statement order (the sell block first). One entry per cross;
      strategy.entry may reverse an open opposite position: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). stdev is the population deviation. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, point target / stop -> ATR fractions.
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

NAME = "fmz_430998_ema_diff_map_cross"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [12.5, 3.0],
    "tp_atr": [5.0, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 20, "sd_len": 2, "lookback": 504, "fast": 50, "slow": 200, "atr_len": 14,
                  "sl_atr": 12.5, "tp_atr": 5.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    sd = c.rolling(int(p["sd_len"])).std(ddof=0)
    lb = int(p["lookback"])
    norm = (sd - sd.rolling(lb).min()) / (sd.rolling(lb).max() - sd.rolling(lb).min())
    mapped = pd.Series(np.where(c > ema, 50 + 50 * norm, 50 - 50 * norm), index=c.index).where(norm.notna())
    e50 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s200 = c.rolling(int(p["slow"])).mean()
    xo = ((e50 > s200) & (e50.shift(1) <= s200.shift(1))).to_numpy()
    xu = ((e50 < s200) & (e50.shift(1) >= s200.shift(1))).to_numpy()
    mv, cv, sv = mapped.to_numpy(), c.to_numpy(dtype=float), s200.to_numpy()
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    w_buy = w_sell = False
    for i in range(m):
        if xu[i]:
            w_sell, w_buy = True, False
        if w_sell and cv[i] < sv[i] and mv[i] > 75:
            se[i], w_sell = True, False
        if xo[i]:
            w_buy, w_sell = True, False
        if w_buy and cv[i] > sv[i] and mv[i] < 25:
            le[i], w_buy = True, False
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    idx = bars_df.index
    le_s, se_s = pd.Series(le, index=idx), pd.Series(se, index=idx)
    return le_s & ~se_s, se_s, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
