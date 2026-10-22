"""SMA 20 / 50 crossings, broker days: the SMA 20 crossing over the SMA 50 goes long, under it short, each with a 150-tick target from the entry (as an ATR multiple); reversing (the stop is na and places
nothing).
Port of FMZ strategy #440810 "动态SMMA与SMA交叉策略Dynamic-SMMA-and-SMA-Crossover-Strategy" (50 SMMA and 20 SMA Crossover with TP and SL).

FMZ source id: 440810

Source
    https://www.fmz.com/strategy/440810 (PineScript v4, FMZ last modified 2024-02-02 11:38:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-146), "SMMA" 50 (an SMA as written), SMA 20; tp 150 (ticks); sl from close[bar_index + 1]
    crossover(sma20, sma50) -> entry Buy, strategy.exit(profit = 150, loss = sl_price);  crossunder -> entry Sell, the same exit;  sl_price := close[bar_index + 1] on signals

Interpretation choices (Pine rules in SURVEY_README.md)
    * close[bar_index + 1] reaches before the first bar, so the stop price is na and the loss leg places
      nothing. Criterion 2: the 150-tick target (15 USD on BTC with 0.1 ticks, about 0.015 of a daily ATR
      near 1000) becomes 0.015 x ATR(14) of the signal bar as a fraction of its close, shifted one bar
      inside stops() and re-based on the fill; the second grid value widens it. The "SMMA" is an SMA as
      written. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440810_sma20_50_cross_tick_target"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_tp": [0.015, 1.0],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"k_tp": 0.015, "slow": 50, "fast": 20, "atr_len": 14}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    lsig = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    ssig = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tp = float(p["k_tp"]) * _rma(tr, int(p["atr_len"])) / c
    return lsig, ssig, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, tp_s = _setup(bars_df, p)
    tp = tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and hv[i] >= x * (1 + t_):
                pos = 0
            elif pos == -1 and lv[i] <= x * (1 - t_):
                pos = 0
        if i + 1 < m and not np.isnan(tp[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, t_ = True, 1, i + 1, tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, t_ = True, -1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": _setup(bars_df, p)[2].shift(1)}


def portfolio_kwargs(**params):
    return {}
