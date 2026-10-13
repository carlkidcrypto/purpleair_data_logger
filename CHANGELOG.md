Last Updated: 2026-10-13 14:53:57 UTC

<a name="v1.6.0a1"></a>
## [v1.6.0a1] - 2026-10-13

### Bug Fixes

* **matter:** make local sensor polling resilient to unreachable sensors ([#490](https://github.com/carlkidcrypto/purpleair_data_logger/issues/490))

### Build System

* **deps:** Bump the python-dependencies group across 1 directory with 3 updates ([#503](https://github.com/carlkidcrypto/purpleair_data_logger/issues/503))

### Chores

* **deps:** update Dependabot schedule to weekly ([#505](https://github.com/carlkidcrypto/purpleair_data_logger/issues/505))

### Documentation

* clarify validate_sensor_data_before_insert docstring ([#508](https://github.com/carlkidcrypto/purpleair_data_logger/issues/508))
* add versioned documentation for v1.6.0a0 ([#485](https://github.com/carlkidcrypto/purpleair_data_logger/issues/485))

### Features

* enhance documentation SEO with metadata, OpenGraph, JSON-LD, and overview ([#507](https://github.com/carlkidcrypto/purpleair_data_logger/issues/507))
* use model alias sonnet across all gh-aw workflows ([#504](https://github.com/carlkidcrypto/purpleair_data_logger/issues/504))
* Migrate gh-aw workflows from claude-sonnet-5 to gpt-6.1-sol ([#496](https://github.com/carlkidcrypto/purpleair_data_logger/issues/496))


<a name="v1.6.0a0"></a>
## [v1.6.0a0] - 2026-09-26

### Bug Fixes

* handle offline devices gracefully, extract publish action, and bump version to 1.6.0a0 ([#454](https://github.com/carlkidcrypto/purpleair_data_logger/issues/454)) ([#478](https://github.com/carlkidcrypto/purpleair_data_logger/issues/478))
* **ci:** invoke pypa publish directly and extract build-distribution action ([#483](https://github.com/carlkidcrypto/purpleair_data_logger/issues/483))
* **ci:** scope verify_syntax push to main to avoid duplicate concurrent runs on PRs ([#482](https://github.com/carlkidcrypto/purpleair_data_logger/issues/482))

### Build System

* **deps:** bump purpleair_api from 1.5.0 to 1.5.1a0 ([#484](https://github.com/carlkidcrypto/purpleair_data_logger/issues/484))
* **deps:** Bump coverage from 7.16.0 to 7.16.1 ([#471](https://github.com/carlkidcrypto/purpleair_data_logger/issues/471))
* **deps:** Bump coverage from 7.16.0 to 7.16.1 in /tests ([#472](https://github.com/carlkidcrypto/purpleair_data_logger/issues/472))
* **deps:** Bump coverage from 7.15.3 to 7.16.0 ([#460](https://github.com/carlkidcrypto/purpleair_data_logger/issues/460))
* **deps:** Bump coverage from 7.15.3 to 7.16.0 in /tests ([#461](https://github.com/carlkidcrypto/purpleair_data_logger/issues/461))
* **deps:** Bump peter-evans/create-pull-request from 7 to 8 ([#437](https://github.com/carlkidcrypto/purpleair_data_logger/issues/437))
* **deps:** Bump actions/deploy-pages from 4 to 5 ([#435](https://github.com/carlkidcrypto/purpleair_data_logger/issues/435))
* **deps:** Bump actions/upload-pages-artifact from 4 to 5 ([#434](https://github.com/carlkidcrypto/purpleair_data_logger/issues/434))
* **deps:** Bump actions/cache from 4 to 6 ([#436](https://github.com/carlkidcrypto/purpleair_data_logger/issues/436))

### Chores

* **docs:** update changelog ([#453](https://github.com/carlkidcrypto/purpleair_data_logger/issues/453))

### Continuous Integration

* remove codeql.yml as repo uses GitHub default CodeQL setup ([#477](https://github.com/carlkidcrypto/purpleair_data_logger/issues/477))

### Documentation

* fix small typos in README and PSQL logger docstring ([#467](https://github.com/carlkidcrypto/purpleair_data_logger/issues/467))
* add versioned documentation for v1.5.0 ([#441](https://github.com/carlkidcrypto/purpleair_data_logger/issues/441))

### Features

* **ci:** backport workflow optimizations, AIC limits, and helper scripts from ezsnmp ([#475](https://github.com/carlkidcrypto/purpleair_data_logger/issues/475))

### Tests

* cover PurpleAirMatterDataLogger._start_http_server ([#468](https://github.com/carlkidcrypto/purpleair_data_logger/issues/468))


<a name="v1.5.0"></a>
## [v1.5.0] - 2026-08-11

### Build System

* **deps:** Bump coverage from 7.15.2 to 7.15.3 in /tests ([#427](https://github.com/carlkidcrypto/purpleair_data_logger/issues/427))
* **deps:** Bump coverage from 7.15.2 to 7.15.3 ([#424](https://github.com/carlkidcrypto/purpleair_data_logger/issues/424))
* **deps:** Bump actions/checkout from 6 to 7 ([#413](https://github.com/carlkidcrypto/purpleair_data_logger/issues/413))

### Chores

* **docs:** update changelog ([#439](https://github.com/carlkidcrypto/purpleair_data_logger/issues/439))

### Documentation

* fix typos and grammar in README, JSONToMatterBridge, and helper comment ([#440](https://github.com/carlkidcrypto/purpleair_data_logger/issues/440))
* fix duplicated word typo in inline comments ([#430](https://github.com/carlkidcrypto/purpleair_data_logger/issues/430))
* fix incorrect Air Quality Sensor device type ID in JSONToMatterBridge.rst ([#428](https://github.com/carlkidcrypto/purpleair_data_logger/issues/428))


<a name="v1.5.0a2"></a>
## [v1.5.0a2] - 2026-08-05

### Chores

* **docs:** update changelog ([#419](https://github.com/carlkidcrypto/purpleair_data_logger/issues/419))

### Documentation

* fix typos and grammar in README, JSONToMatterBridge, and helper comment ([#420](https://github.com/carlkidcrypto/purpleair_data_logger/issues/420))


<a name="v1.5.0a1"></a>
## [v1.5.0a1] - 2026-08-01

### Build System

* **deps:** Bump coverage from 7.15.0 to 7.15.2 ([#385](https://github.com/carlkidcrypto/purpleair_data_logger/issues/385))
* **deps:** Bump coverage from 7.15.0 to 7.15.2 in /tests ([#386](https://github.com/carlkidcrypto/purpleair_data_logger/issues/386))
* **deps:** Bump actions/setup-python from 6 to 7 ([#390](https://github.com/carlkidcrypto/purpleair_data_logger/issues/390))
* **deps:** Bump prometheus-client from 0.25.0 to 0.26.0 ([#395](https://github.com/carlkidcrypto/purpleair_data_logger/issues/395))
* **deps:** Bump prometheus-client from 0.25.0 to 0.26.0 in /tests ([#396](https://github.com/carlkidcrypto/purpleair_data_logger/issues/396))
* **deps:** Bump coverage from 7.14.3 to 7.15.0 in /tests ([#370](https://github.com/carlkidcrypto/purpleair_data_logger/issues/370))
* **deps:** Bump coverage from 7.14.3 to 7.15.0 ([#369](https://github.com/carlkidcrypto/purpleair_data_logger/issues/369))
* **deps:** Bump coverage from 7.14.2 to 7.14.3 ([#356](https://github.com/carlkidcrypto/purpleair_data_logger/issues/356))
* **deps:** Bump carlkidcrypto/os-specific-runner from 2.3.0 to 2.3.1 ([#355](https://github.com/carlkidcrypto/purpleair_data_logger/issues/355))
* **deps:** Bump github/gh-aw-actions/setup from 0.77.5 to 0.81.3 ([#360](https://github.com/carlkidcrypto/purpleair_data_logger/issues/360))

### Documentation

* fix typos, grammar, and docstring inaccuracies ([#358](https://github.com/carlkidcrypto/purpleair_data_logger/issues/358))
* fix typos, docstring gaps, and clarify NULL vs None ([#350](https://github.com/carlkidcrypto/purpleair_data_logger/issues/350))
* fix typos, docstring gaps, and add missing Sphinx RST files ([#348](https://github.com/carlkidcrypto/purpleair_data_logger/issues/348))
* fix typos, grammar, and add missing Loki/Prometheus usage sections ([#346](https://github.com/carlkidcrypto/purpleair_data_logger/issues/346))


<a name="v1.5.0a0"></a>
## [v1.5.0a0] - 2026-06-05

### Bug Fixes

* resolve workflow 0-jobs failure on push triggers ([#303](https://github.com/carlkidcrypto/purpleair_data_logger/issues/303))
* add workflows write permission to recompile_agentic_workflows.yml ([#302](https://github.com/carlkidcrypto/purpleair_data_logger/issues/302))
* correct workflow action versions and invalid permission scope ([#300](https://github.com/carlkidcrypto/purpleair_data_logger/issues/300))
* exclude main branch at trigger level to prevent 0-jobs failure ([#299](https://github.com/carlkidcrypto/purpleair_data_logger/issues/299))
* recompile workflow skip via job-level if + allow dependabot to update agentic workflow files ([#297](https://github.com/carlkidcrypto/purpleair_data_logger/issues/297))
* sync coverage_autofix_every_3_days.lock.yml frontmatter hash ([#293](https://github.com/carlkidcrypto/purpleair_data_logger/issues/293))

### Documentation

* complete incomplete constant comments, fix class docstrings, remove stale inline comments ([#269](https://github.com/carlkidcrypto/purpleair_data_logger/issues/269))
* fix typos, capitalization, and broken error messages in docs and docstrings ([#266](https://github.com/carlkidcrypto/purpleair_data_logger/issues/266))

### Features

* add Python Version Watcher agentic workflow + flow manager gh-aw docs ([#301](https://github.com/carlkidcrypto/purpleair_data_logger/issues/301))
* add Prometheus storage backend for PurpleAir data logger ([#283](https://github.com/carlkidcrypto/purpleair_data_logger/issues/283))
* add Grafana Loki storage backend ([#286](https://github.com/carlkidcrypto/purpleair_data_logger/issues/286))
* add agentic workflow instruction files adapted from ezsnmp ([#255](https://github.com/carlkidcrypto/purpleair_data_logger/issues/255))


<a name="v1.4.2"></a>
## [v1.4.2] - 2026-03-08


<a name="v1.4.1"></a>
## [v1.4.1] - 2026-02-16


<a name="v1.4.0"></a>
## [v1.4.0] - 2025-01-08


<a name="v1.3.3"></a>
## [v1.3.3] - 2024-02-21


<a name="v1.3.2"></a>
## [v1.3.2] - 2024-01-05


<a name="v1.3.1"></a>
## [v1.3.1] - 2023-12-12


<a name="v1.3.0"></a>
## [v1.3.0] - 2023-12-12


<a name="v1.3.0a1"></a>
## [v1.3.0a1] - 2023-11-23


<a name="v1.3.0a0"></a>
## [v1.3.0a0] - 2023-11-11


<a name="v1.2.1"></a>
## [v1.2.1] - 2023-06-13


<a name="v1.2.1a1"></a>
## [v1.2.1a1] - 2023-05-17


<a name="v1.2.0"></a>
## [v1.2.0] - 2023-02-26


<a name="v1.2.0a2"></a>
## [v1.2.0a2] - 2023-02-18


<a name="v1.2.0a0"></a>
## [v1.2.0a0] - 2023-02-12


<a name="v1.1.0"></a>
## [v1.1.0] - 2023-01-26


<a name="v1.0.0"></a>
## [v1.0.0] - 2022-11-10


<a name="v0.0.8b1"></a>
## [v0.0.8b1] - 2022-09-13


<a name="v0.0.7a1"></a>
## [v0.0.7a1] - 2022-08-22


<a name="v0.0.6a1"></a>
## [v0.0.6a1] - 2022-08-12


<a name="v0.0.5-alpha"></a>
## [v0.0.5-alpha] - 2022-07-27


<a name="v0.0.4-alpha"></a>
## [v0.0.4-alpha] - 2022-07-25

### Reverts

* Attempt to use TO_TIMESTAMP(


<a name="v0.0.3-alpha"></a>
## [v0.0.3-alpha] - 2022-07-23


<a name="v0.0.2-alpha"></a>
## [v0.0.2-alpha] - 2022-07-23


<a name="v0.0.1-alpha"></a>
## v0.0.1-alpha - 2022-07-20

