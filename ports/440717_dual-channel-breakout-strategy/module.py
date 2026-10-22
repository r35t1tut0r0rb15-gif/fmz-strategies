"""Double-band extremes, broker days: a close under both the lower Bollinger band (20, 2 x the 20-day average deviation) and the lower Keltner band (20, 1.5 x the averaged ATR) goes long, above both
upper bands short, each with a tight tick bracket from the entry (as ATR multiples); reversing.
Port of FMZ strategy #440717 "Dual Channel Breakout Strategy" (Estratégia de Compra/Venda BB e KC).

FMZ source id: 440717

Source
    https://www.fmz.com/strategy/440717 (PineScript v4, FMZ last modified 2024-02-01 14:43:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-143), BB 20 / 2 (deviation averaged over 20); KC 20 / 1.5 (ATR averaged over 20); take profit 10, stop 20 ("$", passed as ticks)
    buy = close < lower_bb and close < lower_kc -> entry Compra, strategy.exit(profit = 10, loss = 20);  sell = close > upper_bb and close > upper_kc -> entry Venda, the same bracket

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the target and stop are ticks from the entry; the port reads them as ATR(14)
      multiples of the signal bar, target 0.001 and stop 0.002 (1 / 2 USD on BTC with 0.1 ticks against
      a daily ATR near 1000), shifted one bar inside stops() and re-based on the fill; the second grid
      value widens both 200 times. Pine's stdev is the population deviation. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
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

NAME = "fmz_440717_bb_kc_double_extreme_tick_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.002, 0.4],
    "bb_dev": [2.0, 1.5],
}
DEFAULT_PARAMS = {"k_sl": 0.002, "bb_dev": 2.0, "tp_ratio": 0.5, "bb_len": 20, "kc_len": 20, "kc_mult": 1.5,
                  "atr_len": 14}


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
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    nb, nk = int(p["bb_len"]), int(p["kc_len"])
    bas = c.rolling(nb).mean()
    dev = c.rolling(nb).std(ddof=0).rolling(nb).mean()
    ub, lb = bas + dev * float(p["bb_dev"]), bas - dev * float(p["bb_dev"])
    kb = c.rolling(nk).mean()
    ka = _rma(tr, nk).rolling(nk).mean()
    uk, lk = kb + float(p["kc_mult"]) * ka, kb - float(p["kc_mult"]) * ka
    lsig = ((c < lb) & (c < lk)).to_numpy()
    ssig = ((c > ub) & (c > uk)).to_numpy()
    sl = float(p["k_sl"]) * _rma(tr, int(p["atr_len"])) / c
    return lsig, ssig, sl, float(p["tp_ratio"]) * sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
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
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
