"""One-minute bars: three bars after the VWMA 3 of the close crosses over the SMA 266 the strategy goes long, three bars after it crosses under it goes short, each with a fixed-distance target and stop (10000 and 2000 ticks, about 2.7 % and 0.54 % of the source's BTC price); reversing.
Port of FMZ strategy #432773 "Cross Moving Average Strategy" (Cruzamento de Médias Móveis).

FMZ source id: 432773

Source
    https://www.fmz.com/strategy/432773 (PineScript v4, FMZ last modified 2023-11-21 13:33:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 129-154), VWMA 3, SMA 266; signals delayed 3 bars; profit 10000 ticks, loss 2000 ticks
    buy_signal = crossover(vwma(close, 3), sma(close, 266));  sell_signal = crossunder(...)
    buy_signal[3] -> entry Buy, exit(profit = 10000, loss = 2000);  sell_signal[3] -> entry Sell, exit(profit = 10000, loss = 2000)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the profit and loss are tick distances. On the header's BTC_USDT (0.1 tick, about
      37000 USD in the 2023-11-13 .. 20 window) 10000 ticks are 1000 USD and 2000 ticks 200 USD: ported as
      fractions of the fill, 0.027 and 0.0054 (as #437390). The exits are sent on the entry's signal bar and
      stay until filled. The entry comes 3 bars after the cross, as written. REVERSAL INTENDED. No sizing
      code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed fractional bracket from the fill.
    2 generic: PASS, delayed moving-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only; tick distances converted at the source's BTC price).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the fast line vwma(close, 3); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432773_vwma3_sma266_cross_delay3_fixed_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow_len": [266, 200],
    "delay": [3, 0],
}
DEFAULT_PARAMS = {"fast_len": 3, "slow_len": 266, "delay": 3, "tp": 0.027, "sl": 0.0054}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    nf = int(p["fast_len"])
    vs = v.rolling(nf).sum()
    fast = (c * v).rolling(nf).sum() / vs.where(vs != 0)
    slow = c.rolling(int(p["slow_len"])).mean()
    up = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    dn = (fast < slow) & (fast.shift(1) >= slow.shift(1))
    k = int(p["delay"])
    le = up.shift(k, fill_value=False).astype(bool)        # the cross k bars back: known at this bar
    se = dn.shift(k, fill_value=False).astype(bool)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
