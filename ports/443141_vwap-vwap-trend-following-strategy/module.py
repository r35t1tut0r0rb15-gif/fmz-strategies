"""Two-hour bars: three bars in a row with the previous close above its EMA 200 and above the session VWAP of the previous close goes long (not from a short); three bars below both goes short (not from a long); brackets of +3.5 % / -1.4 % for longs and -2.5 % / +0.9 % for shorts from the entry price.
Port of FMZ strategy #443141 "基于VWAP的趋势跟随策略VWAP-Trend-Following-Strategy" (VWAP Trend Follower).

FMZ source id: 443141

Source
    https://www.fmz.com/strategy/443141 (PineScript v4, FMZ last modified 2024-02-29 15:26:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 153-214), price = close[1]; EMA 200; vwap(close[1]); long TP 3.5 % / SL 1.4 %; short TP 2.5 % / SL 0.9 %
    aLong = close[1] > ema(close[1], 200) and close[1] > vwap(close[1]);  entry_long = aLong and aLong[1] and aLong[2]
    if position_size >= 0: entry Long when entry_long, exit(limit = avg x 1.035, stop = avg x 0.986);  if position_size <= 0: entry Short when entry_short, exit(limit = avg x 0.975, stop = avg x 1.009)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long entry is only called while flat or long and the short only while flat or short, so a
      position never reverses: it ends at its bracket. The brackets are levels from the average (fill)
      price, re-sent with the same values: fixed fractions of the fill, exact; the signals follow them, so
      a stopped position re-enters on the next qualifying bar, as Pine's repeated entry does. vwap(close[1])
      is anchored at the broker-day start (as earlier ports) and weighs the previous close with the bar's
      own volume, as written. The date window feeds nothing. 90 % of equity and the commission are
      sizing and costs. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed percent brackets from the fill.
    2 generic: PASS, three-bar trend / VWAP agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 90 % of equity, capital 100, commission 0.04 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
Opposite entries cannot occur (each side only from flat or the same side).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_443141_three_bar_ema200_vwap_trend_pct_brackets_2h"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_tp": [0.035, 0.02],
    "long_sl": [0.014, 0.01],
}
DEFAULT_PARAMS = {"long_tp": 0.035, "long_sl": 0.014, "short_tp": 0.025, "short_sl": 0.009}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    price = c.shift(1)
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vprice = (price * v).groupby(day).cumsum() / cv.where(cv != 0)
    trend = price.ewm(span=200, adjust=False).mean()
    a_l = (price > trend) & (price > vprice)
    a_s = (price < trend) & (price < vprice)
    el = (a_l & a_l.shift(1, fill_value=False) & a_l.shift(2, fill_value=False)).to_numpy()
    es = (a_s & a_s.shift(1, fill_value=False) & a_s.shift(2, fill_value=False)).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    ltp, lsl, stp, ssl = (float(p[k]) for k in ("long_tp", "long_sl", "short_tp", "short_sl"))
    m = len(el)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, up_px, dn_px = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend = pend, 0
            up_px = ov[i] * (1 + ltp) if pos == 1 else ov[i] * (1 + ssl)
            dn_px = ov[i] * (1 - lsl) if pos == 1 else ov[i] * (1 - stp)
        if pos != 0 and (hv[i] >= up_px or lv[i] <= dn_px):    # the bracket ends the trade inside the bar
            pos = 0
        if pos == 0 and i + 1 < m:
            if el[i]:
                le[i], pend = True, 1
            elif es[i]:
                se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    ix = bars_df.index
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=ix).mask(lf, float(p["long_sl"])).mask(sf, float(p["short_sl"]))
    tp_f = pd.Series(np.nan, index=ix).mask(lf, float(p["long_tp"])).mask(sf, float(p["short_tp"]))
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
