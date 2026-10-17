"""Momentum candles on the side of the SMA 200, from flat, with an ATR bracket, broker days: a bullish candle with a
larger body than the previous bar's, closing above the SMA 200, goes long when no trade is open; the bearish mirror
below the SMA goes short; each trade has a stop and a target (pips in the source, ATR multiples here).
Port of FMZ strategy #490805 "移动平均与动量蜡烛趋势跟踪系统-Moving-Average-and-Momentum-Candle-Trend-Following-System" (MA200 + Momentum Candle Strategy (No Duplicate Entry)).

FMZ source id: 490805

Source
    https://www.fmz.com/strategy/490805 (PineScript v5, FMZ last modified 2025-04-16 16:01:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-212), SMA 200, SL 50 pips, TP 100 pips (pip = 10 ticks)
    buy = close > sma200 and close > open and |body| > |previous body|;  sell = the mirror below the SMA
    strategy.opentrades == 0 -> entry + exit(stop = close -+ 50 pips, limit = close +- 100 pips) from the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the pip distances become sl_atr / tp_atr x Wilder ATR(14) of the signal bar: on the author's
      daily TRX_USD (tick 0.00001, price about 0.24) 50 / 100 pips are about 2 % / 4 %, about 0.5 / 1 daily ATR
      (judgement before any backtest). Shifted one bar inside stops(), re-based on the fill (house rule).
    * Entries only when no trade is open: simulate() follows the house bracket on bars (from the fill bar: a bar whose
      low / high reaches the stop or target leaves the trade flat), as the desktop's flat-only bracket ports.
      Opposite entries cannot occur. A buy and a sell cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, pip distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_490805_sma200_momentum_candle_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.5, 1.0],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ma_len": 200, "sl_atr": 0.5, "tp_atr": 1.0, "atr_len": 14}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["ma_len"])).mean()
    body, pbody = (c - o).abs(), (c - o).abs().shift(1)
    buy = ((c > sma) & (c > o) & (body > pbody)).to_numpy()
    sell = ((c < sma) & (c < o) & (body > pbody)).to_numpy()
    frac = (_atr(bars_df, int(p["atr_len"])) / c).to_numpy(dtype=float)
    sl_f, tp_f = p["sl_atr"] * frac, p["tp_atr"] * frac
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and not np.isnan(sl_f[i]) and i + 1 < m:
            if buy[i]:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_f[i], tp_f[i]
            elif sell[i]:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl_f[i], tp_f[i]
    return le, se, sl_f, tp_f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
