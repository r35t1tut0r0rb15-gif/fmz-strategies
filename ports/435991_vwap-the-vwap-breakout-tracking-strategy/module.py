"""Five-minute bars: after a "push" (three rising closes that took the close from under the session VWAP to above it) the push bar's high is saved; the close crossing over it goes long, closed when the close crosses under the VWAP; the mirror push saves a low, and the close crossing under it below the VWAP goes short, closed when the close crosses over the VWAP; reversing.
Port of FMZ strategy #435991 "VWAP突破追踪策略The-VWAP-breakout-tracking-strategy" (VWAP Push).

FMZ source id: 435991

Source
    https://www.fmz.com/strategy/435991 (PineScript v5, FMZ last modified 2023-12-20 16:25:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 191-241), ta.vwap(close) (session); pushes of 3 closes through the VWAP
    is_push_up = close > close[1] > close[2] > close[3] and close[4] < vwap and close[3] > vwap;  hi := is_push_up ? high : hi;  lo := is_push_down and close < vwap ? low : lo
    crossover(close, hi) -> entry Long;  crossunder(close, vwap) -> close Long;  crossunder(close, lo) and close < vwap -> entry Sell;  crossover(close, vwap) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap is the session VWAP, anchored at the broker-day start (as earlier ports); the push tests
      compare the older closes with the CURRENT VWAP, as written. A close acts only on a position the
      bar's entries leave unchanged (call order). REVERSAL INTENDED. 100 % of equity is sizing. FREQ =
      "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWAP push breakouts with VWAP exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 100000, pyramiding 0, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP of the close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435991_vwap_push_high_low_breakout_5m_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "push_len": [3, 2],
}
DEFAULT_PARAMS = {"push_len": 3}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    day = broker_day(c.index)
    cv_ = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv_.where(cv_ != 0)
    k = int(p["push_len"])
    rising = np.logical_and.reduce([(c.shift(j) > c.shift(j + 1)).to_numpy() for j in range(k)])
    falling = np.logical_and.reduce([(c.shift(j) < c.shift(j + 1)).to_numpy() for j in range(k)])
    p_up = rising & (c.shift(k + 1) < vwap).to_numpy() & (c.shift(k) > vwap).to_numpy()
    p_dn = falling & (c.shift(k + 1) > vwap).to_numpy() & (c.shift(k) < vwap).to_numpy()
    hv, lv, cv, wv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float), vwap.to_numpy()
    m = len(cv)
    hi, lw = np.full(m, np.nan), np.full(m, np.nan)
    qh = ql = np.nan
    for i in range(m):
        if p_up[i]:
            qh = hv[i]
        if p_dn[i] and cv[i] < wv[i]:
            ql = lv[i]
        hi[i], lw[i] = qh, ql
    his, lws = pd.Series(hi, index=c.index), pd.Series(lw, index=c.index)
    long_c = ((c > his) & (c.shift(1) <= his.shift(1))).to_numpy()
    exit_l = ((c < vwap) & (c.shift(1) >= vwap.shift(1))).to_numpy()
    short_c = ((c < lws) & (c.shift(1) >= lws.shift(1)) & (c < vwap)).to_numpy()
    exit_s = ((c > vwap) & (c.shift(1) <= vwap.shift(1))).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        changed = False
        if long_c[i] and pos != 1:
            le[i], pos, changed = True, 1, True
        if short_c[i] and pos != -1:
            se[i], le[i], pos, changed = True, False, -1, True
        if changed:
            continue
        if pos == 1 and exit_l[i]:
            lx[i], pos = True, 0
        elif pos == -1 and exit_s[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
