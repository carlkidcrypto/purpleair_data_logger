======================================================
Self-Contained Multi-Language SWIG Bindings & Packages
======================================================

``purpleair_data_logger`` distributes its **C++17** PurpleAir telemetry engine, ``purpleair_api`` C++17 base layer (`v2026.11.11a2` CalSemVer alpha baseline; `PurpleAirAPI`, `PurpleAirReadAPI`, `PurpleAirWriteAPI`, `PurpleAirLocalAPI`), embedded **SQLite3** C amalgamation, JSON configuration validator, and CLI runner as **self-contained packages** across **4 SWIG 4.x target languages**:

1. **Python** (``-python``, self-contained PyPI wheels built via ``cibuildwheel`` + ``auditwheel`` / ``delocate-wheel`` / ``delvewheel``)
2. **JavaScript / Node.js N-API** (``-javascript -napi``, self-contained addon in ``bindings/javascript/``)
3. **C# / .NET 8+** (``-csharp``, self-contained NuGet package with ``runtimes/<rid>/native/`` in ``bindings/csharp/``)
4. **Go** (``-go -cgo -intgosize 64``, self-contained ``cgo`` library bundle in ``bindings/go/``)

Generating All 4 SWIG Target Wrappers
=====================================

.. code-block:: bash

   python3 tools/generate_swig_bindings.py --languages python javascript csharp go --out-dir generated_swig
