.. meta::
   :description: Automated data collectors for PurpleAir sensors. Log real-time and historical air quality data into PostgreSQL, SQLite, CSV, Prometheus, and Matter.
   :keywords: purple air data logger, purpleair data logger, purpleair_data_logger, padls, purpleair postgresql, purpleair prometheus, purpleair sqlite, purpleair csv, air quality logging, carlkidcrypto
   :author: Carlos (@carlkidcrypto)
   :property=og:title: PurpleAir Data Logger (PADLs) — Air Quality Data Collector
   :property=og:description: Automated data loggers for PurpleAir sensors supporting SQLite, PostgreSQL, CSV, Prometheus metrics, and Matter.
   :property=og:type: website
   :property=og:url: https://carlkidcrypto.github.io/purpleair_data_logger/
   :name=twitter:card: summary
   :name=twitter:title: PurpleAir Data Logger (PADLs)
   :name=twitter:description: Automated data loggers for PurpleAir sensors supporting PostgreSQL, SQLite, CSV, and Prometheus.

PurpleAir Data Logger Documentation
===================================

**PurpleAir Data Logger(s) (PADLs)** is an automated suite of data collectors and
telemetry loggers designed to pull readings from `PurpleAir <https://www2.purpleair.com/>`_
air quality sensors and archive them into reliable persistent storage. Whether you run a
single personal sensor or monitor a county-wide sensor network, PADLs keeps your air quality
history accessible and queryable.

Key Features
------------

* **Multiple Storage Backends:** Seamlessly log data to PostgreSQL, SQLite, flat CSV files, or expose Prometheus metrics.
* **Smart Home Integration:** Native export for Matter-enabled smart home systems.
* **Continuous & Scheduled Logging:** Run as a persistent background daemon, containerized service, or cron job.
* **Historical & Real-Time Sync:** Automatically backfill missed timestamps and poll the latest sensor data.

Select a Version
----------------

Select a version of the documentation to browse:

.. VERSION_LIST_START

* `Latest Version <./html/index.html>`_
* `v1.6.0a1 <./html_v1.6.0a1/index.html>`_
* `v1.5.0 <./html_v1.5.0/index.html>`_

.. VERSION_LIST_END

Project Links
-------------

* **Source Code:** `GitHub Repository <https://github.com/carlkidcrypto/purpleair_data_logger>`_
* **Package:** `PyPI Package <https://pypi.org/project/purpleair-data-logger/>`_
* **API Wrapper:** `PurpleAir API Library <https://carlkidcrypto.github.io/purpleair_api/>`_
* **Matter Bridge:** `PurpleAir Matterbridge <https://carlkidcrypto.github.io/purpleair-matterbridge/>`_
* **Maintainer:** `Carlos (@carlkidcrypto) <https://carlkidcrypto.github.io/>`_
