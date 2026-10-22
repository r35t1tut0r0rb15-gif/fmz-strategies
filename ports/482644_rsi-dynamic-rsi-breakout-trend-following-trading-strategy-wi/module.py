"""RSI 14 against its last turning values, 2-day bars: RSI over the last RSI trough value goes long, RSI under the last RSI peak value goes short (the short wins when both hold), each with its stop at the previous bar's low / high and a 4R target from the signal close; reversing.
Port of FMZ strategy #482644 "动态RSI突破趋势跟踪交易策略结合风险收益比优化系统-Dynamic-RSI-Breakout-Trend-Following-Trading-Strategy-with-Risk-Reward-Ratio-Optimization-System" (RSI Breakout Strategy with RR 1:4).

FMZ source id: 482644

Source
    https://www.fmz.com/strategy/482644 (PineScript v6, FMZ last modified 2025-02-19 14:59:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-148), RSI 14; levels 70 / 30 (plots only); stop low[1] / high[1]; RR 1:4
    rsi > rsi[1] and rsi[1] < rsi[2] -> rsi_prev_high := rsi[1];  rsi < rsi[1] and rsi[1] > rsi[2] -> rsi_prev_low := rsi[1]
    rsi > rsi_prev_high -> entry Long + exit(stop = low[1], limit = close + 4 (close - low[1]));  rsi < rsi_prev_low -> entry Short + exit(stop = high[1], limit = close - 4 (high[1] - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, "prev_high" holds the RSI value at the last RSI trough and "prev_low" the value at the
      last peak, so both conditions hold whenever RSI sits between them: the short is the later call and
      wins (as #437773), and a long needs RSI at or above the last peak value. The levels are fixed at the
      signal close and sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). The signals repeat on most bars while held, each re-sending the
      bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing code. Bars are blocks of two
      broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute.
      FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-bar stop and 4R target as fractions of the fill.
    2 generic: PASS, RSI breaks of its last turning values.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482644_rsi14_turn_value_break_prev_bar_stop_4r_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_length": [14, 7],
    "rr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_length": 14, "rr": 4.0, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _last_where(values, mask):
    """The value at the last bar where mask held (a var updated on those bars); NaN before the first."""
    idx = np.maximum.accumulate(np.where(mask, np.arange(len(values)), -1))
    return np.where(idx >= 0, values[np.maximum(idx, 0)], np.nan)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    r1, r2 = r.shift(1), r.shift(2)
    trough = ((r > r1) & (r1 < r2)).to_numpy()
    peak = ((r < r1) & (r1 > r2)).to_numpy()
    r1v = r1.to_numpy(dtype=float)
    ph = pd.Series(_last_where(r1v, trough), index=c.index)      # "rsi_prev_high", as written
    pl = pd.Series(_last_where(r1v, peak), index=c.index)        # "rsi_prev_low"
    lc = r > ph
    sc = r < pl
    se = sc
    le = lc & ~sc                                                # the later (short) call wins
    rr = float(p["rr"])
    l_sl, s_sl = lo.shift(1), h.shift(1)
    lvl = {"l_sl": l_sl, "l_tp": c + rr * (c - l_sl), "s_sl": s_sl, "s_tp": c - rr * (s_sl - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
