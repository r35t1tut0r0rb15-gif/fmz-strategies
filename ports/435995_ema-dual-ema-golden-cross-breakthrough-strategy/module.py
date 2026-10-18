"""Zero-lag EMA crossings of the open price inside a daily session, 1-hour bars: ZLEMA 5 crossing over ZLEMA 34 (or the open crossing over ZLEMA 5 above ZLEMA 34)
between 04:00 and 15:00 UTC goes long; the mirror goes short (reversing); a trade is closed on a bar whose high or low touches a percent stop
(a trailing one from the best high / low since entry) or a percent target, re-expressed from the pip inputs.
Port of FMZ strategy #435995 "双EMA黄金交叉突破策略Dual-EMA-Golden-Cross-Breakthrough-Strategy" ([STRATEGY][RS]MicuRobert EMA cross V2).

FMZ source id: 435995

Source
    https://www.fmz.com/strategy/435995 (PineScript v2, FMZ last modified 2023-12-20 16:34:58).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 116-169), EMA 5 / DEMA 34 of the open (ZLEMA form); session 0400-1500; target 55 pips, stop 22 pips, trailing on
    ma = ema1 + (ema1 - ema2) of the open;  buy = crossover(ma5, ma34) or (crossover(open, ma5) and ma5 > ma34), inside the session;  sell mirrors
    buy_close = low <= apex - sl (trailing) or high >= entry + tp;  apex = the highest high since the fill (renewed on a new buy);  sell_close mirrors;  entry / close "buy", entry / close "sell"

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule: the session is 04:00 to 15:00 in the exchange time zone of the backtest (UTC for the
      Binance runs; the test is on the bar's start hour: 04, 05, ... 14). The apex and entry-price
      variables are followed on every bar, as in the script (stale values stay when flat, so a close
      order can fire right behind an entry: the net result is flat). isnewbuy is true only when the position
      opens from flat. Criterion 2: pip distances (55 / 22 pips of 10 ticks) are re-expressed as
      fractions of the entry price: tp_frac 0.0055 and sl_frac 0.0022 (FX-like values near 1.1; wider
      alternatives in the grid). The exits are rules on bar highs / lows tested at the bar's close and filled at
      the next open: close-based exit signals, not broker stops. REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: ADAPT, pip distances -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trade size and the pip inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435995 (3 members, best partner #436775, Jaccard 0.934); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 04:00-15:00 UTC (the backtest exchange's time zone; no DST); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435995_zlema_open_cross_session"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_frac": [0.0055, 0.01],
    "sl_frac": [0.0022, 0.005],
}
DEFAULT_PARAMS = {"tp_frac": 0.0055, "sl_frac": 0.0022, "len0": 5, "len1": 34, "session_start": 4, "session_end": 15}


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


def _zlema(s, n):
    e1 = s.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    return e1 + (e1 - e2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    ma0, ma1 = _zlema(o, int(p["len0"])), _zlema(o, int(p["len1"]))
    hour = bars_df.index.hour
    sess = (hour >= int(p["session_start"])) & (hour < int(p["session_end"]))
    buy_entry = (((ma0 > ma1) & (ma0.shift(1) <= ma1.shift(1)))
                 | ((o > ma0) & (o.shift(1) <= ma0.shift(1)) & (ma0 > ma1))).fillna(False).to_numpy() & sess
    sel_entry = (((ma0 < ma1) & (ma0.shift(1) >= ma1.shift(1)))
                 | ((o < ma0) & (o.shift(1) >= ma0.shift(1)) & (ma0 < ma1))).fillna(False).to_numpy() & sess
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp_frac"]), float(p["sl_frac"])
    m = len(ov)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    buy_px = sel_px = np.nan
    buy_apex = sel_apex = np.nan
    for i in range(m):
        before = pos
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            e_b, c_b, e_s, c_s = pend
            if e_b and pos <= 0:
                pos = 1
            if c_b and pos == 1:
                pos = 0
            if e_s and pos >= 0:
                pos = -1
            if c_s and pos == -1:
                pos = 0
        held[i] = pos
        new_buy = before == 0 and pos == 1
        new_sel = before == 0 and pos == -1
        if new_buy:
            buy_px = ov[i]
        if new_sel:
            sel_px = ov[i]
        # apex variables are followed on every bar (apex of a long: highest high; of a short: lowest low)
        buy_apex = ov[i] if np.isnan(buy_apex) else (hv[i] if new_buy else (hv[i] if hv[i] >= buy_apex else buy_apex))
        sel_apex = ov[i] if np.isnan(sel_apex) else (lv[i] if new_sel else (lv[i] if lv[i] <= sel_apex else sel_apex))
        buy_close = bool(not np.isnan(buy_px)) and (lv[i] <= buy_apex - buy_px * sl or hv[i] >= buy_px * (1 + tp))
        sel_close = bool(not np.isnan(sel_px)) and (hv[i] >= sel_apex + sel_px * sl or lv[i] <= sel_px * (1 - tp))
        pend = (bool(buy_entry[i]), buy_close, bool(sel_entry[i]), sel_close)
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
