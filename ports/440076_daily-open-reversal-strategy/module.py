"""Daily candle-colour fades with a tick bracket, broker days: from flat (or already long), a red daily candle goes long; a green one goes short; each trade has a 200-tick target and a 1000-tick stop,
re-expressed as ATR multiples.
Port of FMZ strategy #440076 "Daily Open Reversal Strategy" (Daily Open Strategy).

FMZ source id: 440076

Source
    https://www.fmz.com/strategy/440076 (PineScript v4, FMZ last modified 2024-01-26 14:35:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 216-252), previous candle range 0.01 (price units); take profit 200, stop loss 1000 (pips / ticks); date range true
    longTrigger = open - close > 0.01 and close < open -> entry Long when not short;  shortTrigger = close - open > 0.01 and close > open -> entry Short when not long;  exit(loss = 1000, profit = 200) each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.01 range is in price units and becomes a fraction of the close (2.4e-7, the
      BTC reading near 42000: in effect any red or green candle). The bracket is in ticks from the fill;
      the port reads it as ATR(14) multiples of the signal bar, stop 0.1 and target 0.02 (100 / 20 on
      BTC with 0.1 ticks against a daily ATR near 1000), shifted one bar inside stops() and re-based on
      the fill; the second grid value widens both 20 times. An entry is never sent against a held
      position, so trades start only from flat ("Flat" follows the house bracket loop). Opposite entries
      cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. The 100 % of equity size is sizing. Daily bars are broker days, stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit range -> fraction; tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the pip inputs stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440076_daily_candle_fade_tick_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.1, 2.0],
}
DEFAULT_PARAMS = {"k_sl": 0.1, "tp_ratio": 0.2, "range_frac": 2.4e-7, "atr_len": 14}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _levels(bars_df, p):
    c = bars_df["close"]
    sl = (float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / c).to_numpy()
    return sl, float(p["tp_ratio"]) * sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    rf = float(p["range_frac"]) * c
    lt = ((o - c) > rf).to_numpy()
    st = ((c - o) > rf).to_numpy()
    sl, tp = _levels(bars_df, p)
    ov = o.to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            if lt[i]:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif st[i]:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _levels(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
