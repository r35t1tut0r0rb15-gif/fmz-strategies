"""Hourly bars: the first bar of an up bar closing (and with its low) above the EMA 9 and the session VWAP on above-average volume goes long; the first bar of a close under the EMA 9 / 20 and the VWAP on above-average volume, or two red candles in a row, goes short; no signal on the bar after a signal; reversing.
Port of FMZ strategy #452354 "Buy and Sell Volume Heatmap with Real Time Price Strategy" (Buy and Sell Volume Heatmap with Real-Time Price Strategy).

FMZ source id: 452354

Source
    https://www.fmz.com/strategy/452354 (PineScript v5, FMZ last modified 2024-05-24 17:16:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 101-218), EMA 9 / 20; vwap(close); volume SMA 20; heatmap lookback 100 (plots only)
    buy_condition = close > ema9 and close > vwap and volume > sma(volume, 20) and close > open and low > ema9 and low > vwap;  buy_signal = buy_condition and not prev_buy_condition and not signal_occurred
    sell_signal = (sell_condition and not prev_sell_condition and not signal_occurred) or (two red candles and not signal_occurred);  signal_occurred := buy_signal or sell_signal;  entry Buy / entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * signal_occurred is the previous bar's signal, so a signal blocks the next bar's. The previous
      conditions start as na, read as false. The volume heatmap and labels only draw. vwap(close) is the
      session VWAP, anchored at the broker-day start (as earlier ports). When both signals fire the later
      call (short) wins. REVERSAL INTENDED. 10 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, first bars of EMA / VWAP / volume momentum, two-red-candle shorts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20 and as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452354_ema_vwap_volume_first_bar_two_red_short_1h_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "vol_len": [20, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 20, "vol_len": 20}


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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c, v = (bars_df[k] for k in ("open", "low", "close", "volume"))
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    e = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    bc = ((c > a) & (c > e) & vol_ok & (c > o) & (lo > a) & (lo > e)).to_numpy()
    sc = ((c < a) & (c < b) & (c < e) & vol_ok).to_numpy()
    red2 = ((c.shift(1) < o.shift(1)) & (c < o)).to_numpy()
    m = len(bc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    prev_b = prev_s = occurred = False
    pos = 0
    for i in range(m):
        buy = bc[i] and not prev_b and not occurred
        sell = (sc[i] and not prev_s and not occurred) or (red2[i] and not occurred)
        prev_b, prev_s = bc[i], sc[i]
        occurred = buy or sell
        new = pos
        if buy and new != 1:
            new = 1
        if sell and new != -1:
            new = -1
        if new != pos:
            if new == 1:
                le[i] = True
            else:
                se[i] = True
            pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
