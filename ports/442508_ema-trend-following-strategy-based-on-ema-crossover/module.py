"""EMA 21 / 55 trend entries, daily bars, long only: from flat, the EMA 21 above the EMA 55 with the close above the EMA 21 goes long with a stop 3 ATR(14) under the signal close; the close falling
under the EMA 21 closes the trade.
Port of FMZ strategy #442508 "基于EMA平均线交叉的趋势追踪策略Trend-Following-Strategy-Based-on-EMA-Crossover" (EMA cross-over strategy by AP (EMACS-AP)).

FMZ source id: 442508

Source
    https://www.fmz.com/strategy/442508 (PineScript v5, FMZ last modified 2024-02-22 13:59:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-224), EMA 21 / 55; ATR 14; stop 3 ATR; 100 % of equity, capital 100000, commission 0.025; dates dropped
    ema21 > ema55 and close > ema21 and not in trade -> entry long;  strategy.exit(stop = close - 3 atr)
    close < ema21 and in trade -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent once, on the signal bar, from that bar's close and ATR: sl_stop = 3 ATR / close
      of the signal bar, shifted one bar inside stops() and re-based on the fill. Entries come only
      from flat. The date window is dropped. Long only. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. The percent-of-equity size, capital and commission are
      sizing. Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, EMA stack and close position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442508_ema21_55_trend_atr_stop_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [21, 10],
    "slow": [55, 100],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 55, "atr_len": 14, "atr_mult": 3.0}


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


def _fraction(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return float(p["atr_mult"]) * _rma(tr, int(p["atr_len"])) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    go = ((ef > es) & (c > ef)).to_numpy()
    out = (c < ef).to_numpy()
    sl = _fraction(bars_df, p).to_numpy()
    ov, lv = bars_df["open"].to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i and s_ > 0 and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        if pos == 1 and i >= entry_i and out[i]:
            lx[i], pos = True, 0
        elif pos == 0 and go[i] and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _fraction(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
