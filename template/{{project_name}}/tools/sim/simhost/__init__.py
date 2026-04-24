"""Device simulation for native firmware tests.

Usage pattern:
    - For simple deterministic behaviour, use the C++ fakes in
      components/adapters_fake/ directly from GoogleTest.
    - For richer scenarios (recorded IMU traces, fault injection,
      multi-device buses) instantiate a simhost.buses.I2cBus here,
      register device handlers, and drive the firmware via a
      ctypes bridge to a shared-library build of components/core/.
"""
from .buses import I2cBus, SpiBus  # noqa: F401
