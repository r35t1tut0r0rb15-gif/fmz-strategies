"""A Gaussian-weighted 20-bar channel (2 weighted standard deviations) with Stochastic RSI (14 / 14, K 3, D 3), broker days, long only, from 2018: a close above the upper line with K over D buys from flat; a close back under the upper line closes.
Port of FMZ strategy #482786 "Gaussian Channel Trend Following with Stochastic RSI Trading Strategy" (Gaussian Channel + Stoch RSI Strategy).

FMZ source id: 482786

Source
    https://www.fmz.com/strategy/482786 (PineScript v5, FMZ last modified 2025-02-20 11:01:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-171), Gaussian 20 (sigma = length / 6), x 2.0; RSI 14, Stoch 14, K 3, D 3; date range 2018-01-01 .. 2069-01-01; 100 % of equity, commission 0.1 %
    mid = sum(close[i] w_i) / sum(w_i), w_i = exp(-(i - 9.5)^2 / (2 (20/6)^2)), i = 0 .. 19;  std = sqrt(sum(w_i (close[i] - mid)^2) / sum(w_i))
    in range: close > mid + 2 std and k > d and position <= 0 -> entry Long;  close < upper and position > 0 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Gaussian weights are centred on the middle of the 20-bar window, as written (the window still
      ends at the current bar). The stochastic divides by max(range, 1e-10). The date range is kept as
      written (UTC bar times). The entry and the close need opposite sides of the upper line, so they
      never meet. Long only. The 100 % of equity size and capital are sizing; the commission is a cost and
      is not ported (house cost model). Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Gaussian channel breakouts with Stochastic RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported; commission not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: date range 2018-01-01 .. 2069-01-01 (UTC); broker days.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482786_gauss20_weighted_channel_upper_break_stochrsi_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "multiplier": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "multiplier": 2.0, "rsi_length": 14, "stoch_length": 14, "k_length": 3,
                  "d_length": 3}
WINDOW = (pd.Timestamp("2018-01-01", tz="UTC"), pd.Timestamp("2069-01-01", tz="UTC"))


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
    return 100 - 100 / (1 + up / dn)


def _gauss_channel(c, n):
    """The source's Gaussian-weighted mean and deviation over close[0 .. n-1] (age i)."""
    i = np.arange(n, dtype=float)
    w = np.exp(-((i - (n - 1) / 2.0) ** 2) / (2 * (n / 6.0) ** 2))
    v = c.to_numpy(dtype=float)
    m = len(v)
    mid, sd = np.full(m, np.nan), np.full(m, np.nan)
    if m >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)[:, ::-1]   # column i holds close[i]
        mu = win @ w / w.sum()
        var = ((win - mu[:, None]) ** 2) @ w / w.sum()
        mid[n - 1:], sd[n - 1:] = mu, np.sqrt(var)
    return pd.Series(mid, index=c.index), pd.Series(sd, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mid, sd = _gauss_channel(c, int(p["length"]))
    upper = mid + sd * float(p["multiplier"])
    r = _rsi(c, int(p["rsi_length"]))
    ns = int(p["stoch_length"])
    lo_, hi_ = r.rolling(ns).min(), r.rolling(ns).max()
    st = 100 * (r - lo_) / np.maximum(hi_ - lo_, 1e-10)
    k = st.rolling(int(p["k_length"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    t = bars_df.index
    inside = pd.Series((t >= WINDOW[0]) & (t < WINDOW[1]), index=t)
    le = (c > upper) & (k > d) & inside
    lx = (c < upper) & inside
    false = pd.Series(False, index=t)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
