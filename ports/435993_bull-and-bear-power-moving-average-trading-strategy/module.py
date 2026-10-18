"""Bull-power fades with a percent bracket, 30-minute bars, from flat: when the day's running high sits more than a level under the EMA 14, the (reversed) input
goes SHORT with a 7 % stop and a 7 % target; with the input off it goes long. The day's high restarts at 00:00 UTC.
Port of FMZ strategy #435993 "Bull and Bear Power Moving Average Trading Strategy" (Elder Ray (Bull Power) TP and SL).

FMZ source id: 435993

Source
    https://www.fmz.com/strategy/435993 (PineScript v5, FMZ last modified 2023-12-20 16:30:02).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 165-185), EMA 14; trigger -200 (a price unit); reverse true; take profit 7 %, stop 7 %
    DayHigh = day change ? high : max(high, DayHigh[1]);  nRes = DayHigh - ema(close, 14);  pos = nRes < -200 ? 1 : 0;  possig = reverse and pos == 1 ? -1 : pos
    possig == 1 and flat -> entry long, exit(stop = close - 7 %, limit = close + 7 %);  possig == -1 and flat -> entry short, exit(stop = close + 7 %, limit = close - 7 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the trigger -200 is a price unit; the port uses -trigger_frac x close (0.005 is
      the reading, 200 on BTC near 40000; 0.01 a wider one). The day change (dayofmonth) is the calendar day
      of the exchange time zone of the Binance backtest, UTC: the running high restarts at 00:00 UTC (UTC has
      no daylight saving). The bracket is a fraction of the fill price (sl_stop = tp_stop = 0.07);
      entries only from flat ("flat" follows the house bracket on bars). With reverse true only
      shorts can occur. Stop module: portfolio_kwargs {} (driver D4). Stops on 30-minute bars: not
      coarse. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit trigger -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: day reset at 00:00 UTC (the backtest exchange's time zone; no DST); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435993_bull_power_fade_percent_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "reverse": [True, False],
    "trigger_frac": [0.005, 0.01],
}
DEFAULT_PARAMS = {"reverse": True, "trigger_frac": 0.005, "length": 14, "sl": 0.07, "tp": 0.07}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    day = bars_df.index.normalize()                              # the calendar day in UTC
    day_high = h.groupby(day).cummax()
    ema = c.ewm(span=int(p["length"]), adjust=False).mean()
    n_res = (day_high - ema).to_numpy()
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    trig = -float(p["trigger_frac"]) * cv
    base = n_res < trig                                           # pos == 1
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl, tp = float(p["sl"]), float(p["tp"])
    pos, ei = 0, -1
    for i in range(m):
        if pos != 0 and i >= ei:                                  # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - sl) or hv[i] >= e0 * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + sl) or lv[i] <= e0 * (1 - tp)):
                pos = 0
        if pos == 0 and base[i]:
            if p["reverse"]:
                se[i], pos, ei = True, -1, i + 1
            else:
                le[i], pos, ei = True, 1, i + 1
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
