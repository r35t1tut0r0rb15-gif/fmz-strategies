"""N-bar log return breaking the range of its own moving average; exit when it crosses back
through that average (Pine version of Lü's simple volatility strategy).
Port of FMZ strategy #361827 "吕神简易波动率策略Pine语言版本".

Source
    https://www.fmz.com/strategy/361827 (PineScript, author "发明者量化", FMZ last modified
    2022-05-29 20:51:28). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 40-65), N 50
    vix = log(close)/log(close[N-1]) - 1;  vix_ma = sma(vix, N)
    up = highest(vix_ma, N); down = lowest(vix_ma, N)
    flat:  vix crosses above up -> long;  vix crosses below down -> short
    long:  vix crosses below vix_ma -> close_all;  short: vix crosses above vix_ma -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: log(C)/log(C[N-1]) - 1 depends on the price scale (sign flips below 1, blows
      up near 1); the port uses the log return log(C/C[N-1]) (as #200131, the JS version).
    * Unlike #200131 the bands here are the highest/lowest of the MOVING AVERAGE of vix
      (current bar included), as written.
    * Entries only from flat (position_size == 0 branch): opposite entries cannot occur;
      portfolio_kwargs also returns upon_opposite_entry="ignore" (rule 6).
    * Daily bars (backtest period 1d) are broker days (17:00 New York). qty = equity/close is
      sizing.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361827_log_return_ma_range_breakout"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [25, 50, 100],
}
DEFAULT_PARAMS = {"n": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["n"])
    lc = np.log(bars_df["close"])
    vix = lc - lc.shift(n - 1)
    ma = vix.rolling(n).mean()
    up, dn = ma.rolling(n).max(), ma.rolling(n).min()

    def cross_up(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()

    def cross_dn(a, b):
        return ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()

    l_in, s_in = cross_up(vix, up), cross_dn(vix, dn)
    l_out, s_out = cross_dn(vix, ma), cross_up(vix, ma)
    m = len(vix)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos == 0:
            if l_in[i]:
                le[i], pos = True, 1
            elif s_in[i]:
                se[i], pos = True, -1
        elif pos == 1 and l_out[i]:
            lx[i], pos = True, 0
        elif pos == -1 and s_out[i]:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
