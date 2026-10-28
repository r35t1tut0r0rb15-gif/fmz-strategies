"""TradingView-accurate technical indicators for vectorbt.

Plain functions (pandas/numpy in, same type out)::

    import tv_indicators as ti
    bb = ti.bbands(df.close)            # namedtuple: basis, upper, lower, ...
    st = ti.supertrend(df.high, df.low, df.close)

vectorbt indicator classes (parameter grids, crossover helpers)::

    from tv_indicators.vbt import BBANDS
    bb = BBANDS.run(df.close, length=[20, 30], mult=2.0)

See README.md for the full list and the TradingView reference for each.
"""

from ._core import REGISTRY, ma_kind  # noqa: F401
from .bollinger import (  # noqa: F401
    bb_percent_b, bbands, bbtrend, bbw, bbwp, double_bbands, squeeze_momentum,
    ttm_squeeze,
)
from .moving_averages import (  # noqa: F401
    alma, dema, ema, hl2, hlc3, hlcc4, hma, kama, lsma, ma, mcginley, ohlc4,
    rma, sma, tema, vwma, wma,
)
from .oscillators import (  # noqa: F401
    awesome_oscillator, cci, cmo, connors_rsi, coppock, dpo, fisher, macd, mfi,
    mom, roc, rsi, stoch, stoch_rsi, trix, tsi, ultimate_oscillator, wavetrend,
    willr,
)
from .trend import adx, adxr, aroon, dmi, ichimoku  # noqa: F401
from .volatility import (  # noqa: F401
    atr, chandelier_exit, choppiness, donchian, envelope, heikin_ashi,
    historical_volatility, keltner, natr, psar, supertrend, true_range, ut_bot,
    vortex,
)
from .volume import (  # noqa: F401
    accdist, chaikin_osc, cmf, ease_of_movement, efi, klinger, net_volume, nvi, obv,
    pvi, pvt, relative_volume, rolling_vwap, session_ids, vfi, volume_zone_oscillator,
    vwap, vwap_session, williams_ad,
)
from .bill_williams import alligator, fractals, gator, market_facilitation_index  # noqa: F401
from .community import (  # noqa: F401
    alphatrend, atr_stop_loss, chande_kroll_stop, halftrend, ott, qqe, range_filter,
    schaff_trend_cycle, ssl_channel, starc_bands, supertrend_kivanc, trend_magic,
    twin_range_filter, volatility_stop, waddah_attar_explosion, williams_vix_fix,
)
from .filters import (  # noqa: F401
    center_of_gravity, coral, ehma, frama, gmma, itrend, laguerre, laguerre_rsi,
    mavilimw, median, midpoint, midprice, nadaraya_watson, supersmoother, swma, t3,
    thma, trima, ultimate_smoother, vidya, zlema, zlsma,
)
from .momentum import (  # noqa: F401
    accelerator_oscillator, apo, average_day_range, bop, chop_zone, bull_bear_power, chaikin_volatility,
    chande_forecast_oscillator, demarker, disparity_index, efficiency_ratio,
    elder_impulse, elliott_wave_oscillator, intraday_momentum_index,
    inverse_fisher_rsi, kst, macd_v, mass_index, pmo, ppo, pretty_good_oscillator,
    price_oscillator, psychological_line, qstick, random_walk_index, rci,
    relative_volatility_index, rmi, rvgi, smi, smi_ergodic, tdi,
    trend_strength_index, ulcer_index, vhf,
)
from .pivots import pivot_points, pivot_points_session  # noqa: F401
from .statistics import (  # noqa: F401
    beta, correlation, garman_klass, linreg, parkinson, percentrank,
    relative_strength, rogers_satchell, stdev, variance, yang_zhang, zscore,
)

__version__ = "0.2.0"
