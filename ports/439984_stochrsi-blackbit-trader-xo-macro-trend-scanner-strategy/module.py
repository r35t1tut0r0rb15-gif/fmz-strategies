"""First bars of EMA 12 / 25 trends with MACD and EMA 200 filters and a tight percent bracket, 1-hour bars: the first bar of EMA 12 above EMA 25, with the MACD (26, 100, 9) histogram positive and the close
above the EMA 200, goes long; the mirror goes short; each trade has a 0.3 % target and a 0.16 % stop; reversing.
Port of FMZ strategy #439984 "双移动平均线与StochRSI交叉的趋势追踪策略BlackBit-Trader-XO-Macro-Trend-Scanner-Strategy" (BlackBit Trader XO Macro Trend Scanner).

FMZ source id: 439984

Source
    https://www.fmz.com/strategy/439984 (PineScript v5, FMZ last modified 2024-01-25 15:21:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-333), EMA 12 / 25; stoch RSI and alert inputs (unused for orders); EMA filter 200; MACD 26 / 100 / 9; take profit 0.3 %, stop 0.16 %
    countBuy / countSell run counters;  buysignal = countBuy == 1 and countSell == 0 and buy and not buy[1];  lg_rule = buysignal and hist > 0 and close > ema200 -> entry LONG
    while long: exit(loss = entry x 0.16 % / mintick, profit = entry x 0.3 % / mintick);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a percent of the entry price divided back by the tick size, so it is a fixed 0.16 %
      / 0.3 % of the fill (as #437751). The stochastic-RSI alerts feed no order; barstate.isconfirmed
      holds on historical bars. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, EMA run starts, MACD histogram and EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
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

NAME = "fmz_439984_xo_trend_scanner_first_bar_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "takeprofit": [0.003, 0.01],
    "stoploss": [0.0016, 0.005],
}
DEFAULT_PARAMS = {"takeprofit": 0.003, "stoploss": 0.0016, "fast_ema": 12, "slow_ema": 25, "ema_filter": 200,
                  "macd_fast": 26, "macd_slow": 100, "macd_signal": 9}


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
    f = c.ewm(span=int(p["fast_ema"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_ema"]), adjust=False).mean()
    buy, sell = (f > s).to_numpy(), (f < s).to_numpy()
    m = len(c)
    cb = cs = 0
    bsig, ssig = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for i in range(m):
        if buy[i]:
            cb, cs = cb + 1, 0
        if sell[i]:
            cs, cb = cs + 1, 0
        pb = buy[i - 1] if i > 0 else False
        ps = sell[i - 1] if i > 0 else False
        bsig[i] = 0 < cb < 2 and cs < 1 and buy[i] and not pb
        ssig[i] = 0 < cs < 2 and cb < 1 and sell[i] and not ps
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    hist = (macd - macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()).to_numpy()
    ef = c.ewm(span=int(p["ema_filter"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    lg = bsig & (hist > 0) & (cv > ef)
    sh = ssig & (hist < 0) & (cv < ef)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lg, index=ix), false, pd.Series(sh, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stoploss"]), "tp_stop": float(p["takeprofit"])}


def portfolio_kwargs(**params):
    return {}
