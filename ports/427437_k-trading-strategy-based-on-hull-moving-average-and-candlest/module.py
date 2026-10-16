"""HMA vs daily candle: with the bar's open above the Hull MA 50 of opens, the Hull MA above the
reference daily open and the open rising, go long; the mirror goes short; each side is closed when
the opposite alignment (without the rising / falling test) appears.
Port of FMZ strategy #427437 "Trading Strategy Based on Hull Moving Average and Candlestick".

FMZ source id: 427437

Source
    https://www.fmz.com/strategy/427437 (PineScript v4, FMZ last modified 2023-09-21 10:31:58).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 126-141), HMA 50, resolution "D", source open
    HMA = hma(open, 50); Candle = security(ticker, "D", open, gaps_off, lookahead_off)
    open < HMA and HMA < Candle -> close long; open > HMA and HMA > Candle -> close short
    open > HMA and HMA > Candle and open > open[1] -> entry long; the mirror -> entry short

Interpretation choices (Pine rules in SURVEY_README.md, skill section 4)
    * lookahead_off on history: the daily open seen by a 2-hour bar is that of the last broker day
      that has ENDED by the bar's close (day end 17:00 America/New_York, a clock time); on the last
      bar of a day that day's open is seen (it has just ended), as TradingView shows it.
    * hma(x, n) = wma(2 wma(x, n / 2) - wma(x, n), round(sqrt(n))), n / 2 rounded down.
    * The closes come before the entries in the script; a reversal on one bar: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the daily open only once the day has ended.
    2 generic: PASS, comparisons of the instrument's own prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, per-order commission and slippage stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the reference is the broker day's open (17:00 America/New_York, DST by the zone), not a venue open.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427437_hma_vs_daily_open"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [50, 25, 100],
}
DEFAULT_PARAMS = {"period": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["period"])
    o = bars_df["open"]
    hma = _wma(2 * _wma(o, n // 2) - _wma(o, n), int(round(np.sqrt(n))))
    lab = broker_day(bars_df.index)
    day_open = o.groupby(lab).first()
    end_lab = broker_day(bars_df.index + pd.Timedelta(FREQ))
    pos_d = np.searchsorted(day_open.index.values, end_lab.values, side="left") - 1
    candle = np.where(pos_d >= 0, day_open.to_numpy()[np.clip(pos_d, 0, None)], np.nan)
    ov, hv = o.to_numpy(dtype=float), hma.to_numpy()
    o1 = np.concatenate(([np.nan], ov[:-1]))
    up_al = (ov > hv) & (hv > candle)
    dn_al = (ov < hv) & (hv < candle)
    long_c, short_c = up_al & (ov > o1), dn_al & (ov < o1)
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and dn_al[i]:
            pos = 0
        elif pos == -1 and up_al[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
