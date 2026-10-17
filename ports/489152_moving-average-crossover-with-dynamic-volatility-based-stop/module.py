"""SMA 50 below SMA 200 with RSI above 30, long only, with an ATR bracket, broker days: whenever SMA 50 is below SMA 200
and RSI 14 is above 30 the strategy is long (re-entering after an exit); each trade has a stop 1 ATR and a target
1.5 ATR away (re-placed every bar in the source, fixed at the signal bar here).
Port of FMZ strategy #489152 "移动平均线交叉与动态波动率止损量化策略-Moving-Average-Crossover-with-Dynamic-Volatility-Based-Stop-Loss-Strategy" (VS-NTC> NASDQ100 Long MA+RSI+ATR).

FMZ source id: 489152

Source
    https://www.fmz.com/strategy/489152 (PineScript v6, FMZ last modified 2025-04-02 11:08:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 162-212), SMA 50 / 200, RSI 14, ATR 14 x 1, RR 1.5
    long = sma50 < sma200 and rsi > 30 -> entry long   (shortCondition = false)
    long held, every bar: exit(stop = avg - 1 ATR, limit = avg + 1.5 ATR)   (current ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the long condition is SMA 50 BELOW SMA 200 (a counter-trend long), kept.
    * The bracket is relative to the fill but uses the current ATR every bar (a moving level): mark
      trailing_stop_pending; the port fixes it at the signal bar's ATR: sl_stop = ATR / close, tp_stop = 1.5 x that,
      shifted one bar inside stops(), re-based on the fill.
    * Every condition bar is an entry (re-entering the bar after a stop or target). Long only. Stop module:
      portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute; FREQ = "1D" from the backtest header: coarse_bar_stop. The title's NASDAQ 100 is a label.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, SMAs, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489152_sma_50_below_200_rsi_atr_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.0, 2.0],
    "rr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"sma_short": 50, "sma_long": 200, "rsi_len": 14, "atr_period": 14, "atr_mult": 1.0, "rr": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s, l_ = c.rolling(int(p["sma_short"])).mean(), c.rolling(int(p["sma_long"])).mean()
    long_c = ((s < l_) & (_rsi(c, int(p["rsi_len"])) > 30)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["atr_mult"] * _atr(bars_df, int(p["atr_period"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": (p["rr"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
