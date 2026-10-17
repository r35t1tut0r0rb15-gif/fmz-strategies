"""EMA 9 / 21 crosses with RSI 14 on the same side of 50, reversing, with a 25-point stop and a 125-point target read
as 0.1 / 0.5 ATR, daily bars.
Port of FMZ strategy #482450 "动态EMA交叉与RSI协同交易系统-Dynamic-EMA-Crossover-with-RSI-Synergy-Trading-System" (Lukhi EMA Crossover_TWL Strategy).

FMZ source id: 482450

Source
    https://www.fmz.com/strategy/482450 (PineScript v6, FMZ last modified 2025-02-18 14:57:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-153), EMA 9 / 21, RSI 14, stop 25 points, target 5000 / (1000 / 25)
= 125 points
    crossover(ema9, ema21) and rsi > 50 -> entry long with exit(stop = close - 25, limit = close + 125)
    crossunder and rsi < 50 -> entry short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 25 / 125-point distances are price units (criterion 2). On the backtest market (BTC_USDT daily, ATR in the
      thousands) they would be a few hundredths of an ATR; the script's comments name a Nifty option lot, so they
      are judged on the Nifty index's daily bars (ATR about 250 points): 0.1 ATR stop, 0.5 ATR target (as #489333,
      the market named by the source when the backtest market makes the units absurd).
    * The bracket is placed with the entry from the signal bar (ATR / close, shifted one bar inside stops(),
      re-based on the fill; house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, EMAs, RSI and ATR multiples (the point distances converted).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot size 1 and the INR risk arithmetic quoted; the bracket via stops(), in original_sizing.txt.
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

NAME = "fmz_482450_ema9_21_cross_rsi50_point_bracket_atr"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.1, 1.0],
    "tp_atr": [0.5, 2.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "atr_len": 14, "sl_atr": 0.1, "tp_atr": 0.5}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi > 50)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_atr"] * a, "tp_stop": p["tp_atr"] * a}


def portfolio_kwargs(**params):
    return {}
