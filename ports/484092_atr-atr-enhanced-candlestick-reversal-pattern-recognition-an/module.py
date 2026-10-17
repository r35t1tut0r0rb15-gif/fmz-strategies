"""Wide-range hammers and shooting stars with a bar-extreme ATR stop and a 2.5 ATR target, broker days: a hammer (lower
wick over twice the body, upper wick under the body, range over 1.5 ATR) that turns green goes long with the stop 1.5
ATR under its low; a shooting star turning red goes short with the stop 1.5 ATR over its high.
Port of FMZ strategy #484092 "ATR增强型蜡烛反转模式识别与风险管理策略-ATR-Enhanced-Candlestick-Reversal-Pattern-Recognition-and-Risk-Management-Strategy" (Hammers & Stars Strategy).

FMZ source id: 484092

Source
    https://www.fmz.com/strategy/484092 (PineScript v5, FMZ last modified 2025-02-28 09:48:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 216-249), ATR 14, range > 1.5 ATR, stop 1.5 ATR beyond the extreme, target
2.5 ATR
    hammer = lowerWick > 2 x body and upperWick < body and range > 1.5 ATR;  signal = hammer and crossover(close, open)
    star = upperWick > 2 x body and lowerWick < body and range > 1.5 ATR;  signal = star and crossunder(close, open)
    every bar: exit(long: stop = low - 1.5 ATR, limit = close + 2.5 ATR; short: stop = high + 1.5 ATR, limit = close -
    2.5 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(close, open): close > open now and close <= open on the previous bar.
    * The exits are re-issued every bar from the current bar (moving): fixed at the signal bar, mark
      trailing_stop_pending: long sl = (close - low + 1.5 ATR) / close, tp = 2.5 ATR / close (short mirrored), picked by
      the signal's side, shifted one bar inside stops() and re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED); the two patterns cannot fall on one bar. Stop module: portfolio_kwargs {}
      (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (re-issue marked).
    2 generic: PASS, candle proportions and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484092_wide_hammer_star_bracket"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "range_atr": [1.5, 1.0],
    "tp_atr": [2.5, 4.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "range_atr": 1.5, "sl_atr": 1.5, "tp_atr": 2.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    atr = _atr(bars_df, int(p["atr_len"]))
    body = (c - o).abs()
    upper = h - np.maximum(c, o)
    lower = np.minimum(c, o) - lo
    wide = (h - lo) > p["range_atr"] * atr
    hammer = (lower > 2 * body) & (upper < body) & wide
    star = (upper > 2 * body) & (lower < body) & wide
    x_up = (c > o) & (c.shift(1) <= o.shift(1))
    x_dn = (c < o) & (c.shift(1) >= o.shift(1))
    return (hammer & x_up).astype(bool), (star & x_dn).astype(bool), atr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, atr = _signals(bars_df, p)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sl = ((c - lo + p["sl_atr"] * atr) / c).where(long_e, ((h + p["sl_atr"] * atr - c) / c).where(short_e)).shift(1)
    tp = (p["tp_atr"] * atr / c).where(long_e | short_e).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
