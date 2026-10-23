"""45-minute bars: the SSL channel (SMA 12 of highs / SMA 13 of lows) pointing up while the EMA 6 of the 13-bar rate of change is beyond +-2 %, or Chaikin money flow 20 crossing over 0.04, goes long; the channel pointing down while moving, or the money flow crossing under 0.02, goes short; a 2 % stop from the entry; reversing.
Port of FMZ strategy #438772 "Spiral Breakout Moving Average Strategy" (SSL Chaikin BF).

FMZ source id: 438772

Source
    https://www.fmz.com/strategy/438772 (PineScript v4, FMZ last modified 2024-01-15 11:45:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 161-255), Chaikin MF 20, thresholds 0.04 / 0.02; SSL 12 / 13; ROC 13, 4 % change; stop 2 %
    long = sslUp > sslDown and isMoving() or crossover(mf, 0.04);  short = sslUp < sslDown and isMoving() or crossunder(mf, 0.02)
    entry L when long;  entry S when short;  exit(L SL, stop = position_avg_price * 0.98, when = since_longEntry > 0);  exit(S SL, stop = position_avg_price * 1.02, ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * v4 integer division: roclength / 2 = 6 and pcntChange / 2 = 2. When both sides signal on one
      bar the later call (short) wins. The stops are fixed at 2 % of the average entry price; their
      "in signal" gate is on whenever the position is open (it follows the same long / short bars);
      Pine sends the stop from the bar after the fill, the port arms it at the fill (2 % on 45-minute
      bars). The test-period inputs feed nothing (testPeriod() is true). REVERSAL INTENDED. 100 % of
      equity and the commission are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). FREQ
      = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 2 % stop from the fill.
    2 generic: PASS, SSL channel direction with momentum, or Chaikin money-flow crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent_of_equity 100 and commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow sum(ad, 20) / sum(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438772_ssl_roc_chaikin_mf_cross_2pct_stop_45m_reversal"
FAMILY = "ssl_hybrid"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.02, 0.04],
    "cmf_len": [20, 10],
}
DEFAULT_PARAMS = {"cmf_len": 20, "upper": 0.04, "lower": 0.02, "len1": 12, "len2": 13,
                  "roc_len": 13, "pcnt": 4, "sl_pct": 0.02}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    rng = h - lo
    ad = ((2 * c - lo - h) / rng.where(rng != 0) * v).where(rng != 0, 0.0)
    n = int(p["cmf_len"])
    vs = v.rolling(n).sum()
    mf = ad.rolling(n).sum() / vs.where(vs != 0)
    sh, sl_ = h.rolling(int(p["len1"])).mean(), lo.rolling(int(p["len2"])).mean()
    shv, slv, cv = sh.to_numpy(), sl_.to_numpy(), c.to_numpy()
    m = len(cv)
    hlv = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cv[i] > shv[i]:
            q = 1
        elif cv[i] < slv[i]:
            q = -1
        hlv[i] = q
    ssl_dn = np.where(hlv < 0, shv, slv)
    ssl_up = np.where(hlv < 0, slv, shv)
    rl = int(p["roc_len"])
    roc = 100 * (c - c.shift(rl)) / c.shift(rl)
    emaroc = roc.ewm(span=max(rl // 2, 1), adjust=False).mean()
    half = int(p["pcnt"]) // 2
    moving = ((emaroc > half) | (emaroc < -half)).to_numpy()
    up_x = ((mf > float(p["upper"])) & (mf.shift(1) <= float(p["upper"]))).to_numpy()
    dn_x = ((mf < float(p["lower"])) & (mf.shift(1) >= float(p["lower"]))).to_numpy()
    long_ = ((ssl_up > ssl_dn) & moving) | up_x
    short_ = ((ssl_up < ssl_dn) & moving) | dn_x
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(long_ & ~short_, index=ix), false, pd.Series(short_, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
