"""Trigger bars beyond the EMA 5 and the Bollinger bands (20 / 1.5), 1-hour bars: after a bar entirely over the EMA 5 and the upper band, a close back under that bar's close with a low under its low goes short, stopped at the trigger bar's high with a 1000-point target (0.0238 at BTC 42000); the mirror under the lower band goes long; stops and targets are bar-close tests on the high / low.
Port of FMZ strategy #453267 "EMA与布林带突破策略-EMA-and-Bollinger-Bands-Breakout-Strategy" (Nifty Bank Strategy (EMA 5 and Bollinger trigger bars)).

FMZ source id: 453267

Source
    https://www.fmz.com/strategy/453267 (PineScript v5, FMZ last modified 2024-06-03 16:23:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-186), EMA 5; Bollinger 20 / 1.5; target 1000 points; stop at the trigger bar's high / low
    not in trade: low > ema5 and low > upper -> short trigger (high, low, close);  else high < ema5 and high < lower -> long trigger
    not in trade and close < trigger close and low < trigger low -> entry Short, stop = trigger high, target = close - 1000;  the mirror -> entry Long
    in a short: high >= stop -> close Short, else low <= target -> close Short;  the mirror for a long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The in-trade flag, the trigger levels and the bar-close exit tests are followed bar by bar as
      written, beside the actual position: the management runs on the entry's own bar too, where a
      close finds no trade yet but still clears the flag (the order then fills and the trade is held
      without management until a later entry call). The 1000-point target is a price amount, read
      against BTC near 42000 like other price units (#440456): the port sets it at the fraction
      1000 / 42000 of the signal close. The exits are close calls filled at the next open. REVERSAL
      INTENDED (an opposite entry can meet such an unmanaged trade). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exit tests are bar-close tests.
    2 generic: PASS, trigger-bar breakdowns beyond the EMA and bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453267_ema5_bollinger_trigger_bar_break_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [1.5, 2.0],
    "ema_len": [5, 10],
    "tgt_frac": [0.0238, 0.01],
}
DEFAULT_PARAMS = {"bb_mult": 1.5, "ema_len": 5, "tgt_frac": 0.0238, "bb_len": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up_t = ((lo > ema) & (lo > basis + dev) & (h > basis + dev)).to_numpy()
    dn_t = ((h < ema) & (h < basis - dev) & (lo < basis - dev)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tf = float(p["tgt_frac"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend = 0, 0
    in_trade, is_long = False, False
    th = tl = tc = stop = tgt = np.nan
    for i in range(m):
        if pend in (1, -1):
            pos = pend
        elif pend == 2:
            pos = 0
        pend = 0
        cur = pos
        if not in_trade:
            if up_t[i]:
                tl, th, tc = lv[i], hv[i], cv[i]
            elif dn_t[i]:
                th, tl, tc = hv[i], lv[i], cv[i]
        if not in_trade and not np.isnan(tc) and cv[i] < tc and lv[i] < tl:
            stop, tgt = th, cv[i] * (1 - tf)
            if cur != -1:
                cur = -1
            in_trade, is_long = True, False
            th = tl = tc = np.nan
        if not in_trade and not np.isnan(tc) and cv[i] > tc and hv[i] > th:
            stop, tgt = tl, cv[i] * (1 + tf)
            if cur != 1:
                cur = 1
            in_trade, is_long = True, True
            th = tl = tc = np.nan
        if in_trade and not is_long:
            if hv[i] >= stop or lv[i] <= tgt:
                in_trade = False
                if pos == -1 and cur == -1:
                    cur = 0                  # the close acts only on a short held into the bar
        if in_trade and is_long:
            if lv[i] <= stop or hv[i] >= tgt:
                in_trade = False
                if pos == 1 and cur == 1:
                    cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        if cur != pos:
            pend = 2 if cur == 0 else cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
