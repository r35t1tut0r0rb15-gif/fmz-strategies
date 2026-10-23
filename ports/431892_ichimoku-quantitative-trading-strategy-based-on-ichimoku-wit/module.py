"""Ichimoku "Price X Kumo" signal (the script's default of many): the close above the higher edge of the cloud drawn 26 bars back (Senkou A of Tenkan 9 / Kijun 26, Senkou B 52) goes long, the close under its lower edge goes short, hourly bars; reversing.
Port of FMZ strategy #431892 "基于Ichimoku的多信号量化交易策略Quantitative-Trading-Strategy-Based-on-Ichimoku-with-Multiple-Signals" (The Strategy - Ichimoku Kinko Hyo and more).

FMZ source id: 431892

Source
    https://www.fmz.com/strategy/431892 (PineScript v4, FMZ last modified 2023-11-13 10:24:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 215-850), Tenkan 9, Kijun 26, Senkou B 52, shift 26; signal "Price X Kumo sig"; filters "---"; entry type Both; TP / SL off; backtest switch off
    kumo_high = max(SA[25], SB[25]), kumo_low = min(SA[25], SB[25]);  opt_sig_buy = close > kumo_high, opt_sig_sell = close < kumo_low
    entry os_buy when opt_sig_buy (filters "---" = true);  entry os_sell when opt_sig_sell;  close os_buy when (exit filters or not_both) ? opt_sig_sell : na

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default signal is ported; the other 23 signal options and the filters are inputs left at
      "---". With entry type "Both" and the exit filters "---" the strategy.close conditions are
      "false ? sell : na", so no close is ever sent: a position ends only by the opposite entry.
      TP / SL are disabled (na), so strategy.exit sends nothing. backtest = false runs the branch with no
      date window. pyramiding is the default 1, so a repeated same-side entry adds nothing. Volume appears
      only in the Klinger part of the unselected CB/CS signal: not used. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price against the Ichimoku cloud.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 2018 .. 2021 window applies only with backtest = true, which is off).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431892_ichimoku_price_vs_kumo_state_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kijun_len": [26, 30],
    "senkou_b_len": [52, 60],
}
DEFAULT_PARAMS = {"tenkan_len": 9, "kijun_len": 26, "senkou_b_len": 52, "shift": 26}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    tk, kj, sb = mid(int(p["tenkan_len"])), mid(int(p["kijun_len"])), mid(int(p["senkou_b_len"]))
    sa = (tk + kj) / 2
    k = int(p["shift"]) - 1
    sa_k, sb_k = sa.shift(k), sb.shift(k)
    kumo_high = pd.concat([sa_k, sb_k], axis=1).max(axis=1, skipna=False)
    kumo_low = pd.concat([sa_k, sb_k], axis=1).min(axis=1, skipna=False)
    buy = (c > kumo_high).to_numpy()
    sell = (c < kumo_low).to_numpy()
    m = len(buy)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        elif sell[i] and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
