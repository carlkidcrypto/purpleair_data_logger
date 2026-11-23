Last Updated: 2026-11-23 21:54:20 UTC

# Changelog

<a name="v2026.11.22b0"></a>
## [v2026.11.22b0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.6.0...v2026.11.22b0) (2026-11-23)

### Changes

#### Bug Fixes

- fix(ci): switch PyPI/TestPyPI workflows to cibuildwheel for native SWIG wheels ([#567](https://github.com/carlkidcrypto/purpleair_data_logger/issues/567))
- fix(ci): provision purpleair_api C++17 source and build deps in Sphinx workflow ([#544](https://github.com/carlkidcrypto/purpleair_data_logger/issues/544))

#### Build System

- build(deps): Bump coverage in /tests in the python-dependencies group ([#561](https://github.com/carlkidcrypto/purpleair_data_logger/issues/561))
- build(deps): Bump coverage ([#560](https://github.com/carlkidcrypto/purpleair_data_logger/issues/560))
- build(deps): Bump the python-dependencies group with 7 updates ([#541](https://github.com/carlkidcrypto/purpleair_data_logger/issues/541))
- build(deps): Bump coverage in /tests in the python-dependencies group ([#540](https://github.com/carlkidcrypto/purpleair_data_logger/issues/540))
- build(deps): Bump codecov/codecov-action from 5.4.0 to 7.1.1 ([#539](https://github.com/carlkidcrypto/purpleair_data_logger/issues/539))
- build(deps): Bump carlkidcrypto/os-specific-runner from 2.4.0 to 2.5.0 ([#538](https://github.com/carlkidcrypto/purpleair_data_logger/issues/538))
- build(deps): Bump carlkidcrypto/os-specific-runner from 2.4.0 to 2.5.0 ([#530](https://github.com/carlkidcrypto/purpleair_data_logger/issues/530))
- build(deps): Bump sphinx ([#521](https://github.com/carlkidcrypto/purpleair_data_logger/issues/521))
- build(deps): Bump the python-dependencies group across 1 directory with 3 updates ([#523](https://github.com/carlkidcrypto/purpleair_data_logger/issues/523))
- build(deps): Bump coverage ([#524](https://github.com/carlkidcrypto/purpleair_data_logger/issues/524))

#### Code Refactoring

- refactor(agentics): rename docs continuous improvement workflow to docs_continuous_improvement.md ([#531](https://github.com/carlkidcrypto/purpleair_data_logger/issues/531))

#### Continuous Integration

- ci: configure Codecov coverage uploads with if: always() and require_head: false ([#533](https://github.com/carlkidcrypto/purpleair_data_logger/issues/533))
- ci: synchronize verify_syntax workflow with yamllint and actionlint validation ([#535](https://github.com/carlkidcrypto/purpleair_data_logger/issues/535))

#### Documentation Updates

- docs(srs): update Requirements.rst for cibuildwheel packaging and caller-side PyPI OIDC ([#569](https://github.com/carlkidcrypto/purpleair_data_logger/issues/569))
- docs(readme): add TestPyPI version badge ([#568](https://github.com/carlkidcrypto/purpleair_data_logger/issues/568))
- docs: improve PurpleAirDataLogger docstrings ([#555](https://github.com/carlkidcrypto/purpleair_data_logger/issues/555))
- docs: standardize README status badges ([#549](https://github.com/carlkidcrypto/purpleair_data_logger/issues/549))
- docs: clarify CSV data logger docstrings ([#545](https://github.com/carlkidcrypto/purpleair_data_logger/issues/545))
- docs: clarify Matter HTTP API responses ([#542](https://github.com/carlkidcrypto/purpleair_data_logger/issues/542))
- docs: clarify Loki logger docstrings ([#536](https://github.com/carlkidcrypto/purpleair_data_logger/issues/536))
- docs(github): update issue templates with AI-assisted triage notices ([#534](https://github.com/carlkidcrypto/purpleair_data_logger/issues/534))
- docs: document Matter logger retry and offline options ([#529](https://github.com/carlkidcrypto/purpleair_data_logger/issues/529))
- docs: add Prometheus constants module to Sphinx toctree ([#522](https://github.com/carlkidcrypto/purpleair_data_logger/issues/522))
- docs: add versioned documentation for v1.6.0 ([#526](https://github.com/carlkidcrypto/purpleair_data_logger/issues/526))

#### Features

- feat(core,gui,swig): port C++17 telemetry engine, 4-language SWIG bindings, CLI, and Studio GUI from ezsnmp_data_logger ([#537](https://github.com/carlkidcrypto/purpleair_data_logger/issues/537))
- feat(ci): configure Codecov test coverage uploads and status reporting for Python test suite ([#532](https://github.com/carlkidcrypto/purpleair_data_logger/issues/532))

#### Maintenance

- chore(release): prepare beta release v2026.11.22b0 ([#566](https://github.com/carlkidcrypto/purpleair_data_logger/issues/566))
- chore(ci): bump shared-workflows to 22f04e2 and adopt caller-side PyPI OIDC publish ([#565](https://github.com/carlkidcrypto/purpleair_data_logger/issues/565))
- chore(ci): adopt shared-workflows Tier 2/3 reusable SWIG workflow, gh-aw fragments, and SHA pins ([#559](https://github.com/carlkidcrypto/purpleair_data_logger/issues/559))
- chore(ci): adopt shared-workflows Tier 1 actions, reusable workflows, and preflight checklist ([#558](https://github.com/carlkidcrypto/purpleair_data_logger/issues/558))
- chore(release): bump version to 2026.11.18 ([#552](https://github.com/carlkidcrypto/purpleair_data_logger/issues/552))
- chore(ci): migrate PyPI, TestPyPI, and Sphinx workflows to shared-workflows ([#554](https://github.com/carlkidcrypto/purpleair_data_logger/issues/554))
- chore(ci): migrate verify_syntax, black, and copilot-setup-steps to shared-workflows ([#553](https://github.com/carlkidcrypto/purpleair_data_logger/issues/553))
- chore(ci): bump shared-workflows SHA to 88de7dd ([#551](https://github.com/carlkidcrypto/purpleair_data_logger/issues/551))
- chore(ci): adopt carlkidcrypto/shared-workflows ([#550](https://github.com/carlkidcrypto/purpleair_data_logger/issues/550))
- chore(aw): recompile agentic workflows with gh-aw v1.2.2 ([#547](https://github.com/carlkidcrypto/purpleair_data_logger/issues/547))
- chore(changelog): standardize git-chglog config, template, and workflow ([#546](https://github.com/carlkidcrypto/purpleair_data_logger/issues/546))
- chore(release): adopt SemVer-compliant CalVer versioning scheme (2026.11.3a0) ([#528](https://github.com/carlkidcrypto/purpleair_data_logger/issues/528))
- chore(docs): update changelog ([#527](https://github.com/carlkidcrypto/purpleair_data_logger/issues/527))

#### Tests

- test(cpp): reach 100% test coverage across all C++17 engine and header files ([#543](https://github.com/carlkidcrypto/purpleair_data_logger/issues/543))

---
<a name="v1.6.0"></a>
## [v1.6.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.6.0a1...v1.6.0) (2026-11-02)

### Changes

#### Bug Fixes

- fix(aw): allow all tools, add go network preset, and ignore restored skills ([#519](https://github.com/carlkidcrypto/purpleair_data_logger/issues/519))

#### Build System

- build(deps): Bump black ([#513](https://github.com/carlkidcrypto/purpleair_data_logger/issues/513))
- build(deps): Bump carlkidcrypto/os-specific-runner from 2.3.1 to 2.4.0 ([#512](https://github.com/carlkidcrypto/purpleair_data_logger/issues/512))

#### Continuous Integration

- ci(aw): report noop runs to tracking issue and give coverage workflows Codecov data ([#514](https://github.com/carlkidcrypto/purpleair_data_logger/issues/514))

#### Documentation Updates

- docs: clarify Loki logger docstrings ([#511](https://github.com/carlkidcrypto/purpleair_data_logger/issues/511))
- docs: add versioned documentation for v1.6.0a1 ([#509](https://github.com/carlkidcrypto/purpleair_data_logger/issues/509))

#### Features

- feat: migrate release scripts to standardized release_tools ([#516](https://github.com/carlkidcrypto/purpleair_data_logger/issues/516))

#### Maintenance

- chore(release): bump version to 1.6.0, pin purpleair_api 1.5.1, and sync supported Python versions ([#525](https://github.com/carlkidcrypto/purpleair_data_logger/issues/525))
- chore(sonar): exclude docs from sonarqube analysis and duplication checks ([#518](https://github.com/carlkidcrypto/purpleair_data_logger/issues/518))
- chore(github): sync issue templates with ezsnmp conventions ([#515](https://github.com/carlkidcrypto/purpleair_data_logger/issues/515))

#### Updates

- [changelog] Update CHANGELOG.md ([#510](https://github.com/carlkidcrypto/purpleair_data_logger/issues/510))

---
<a name="v1.6.0a1"></a>
## [v1.6.0a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.6.0a0...v1.6.0a1) (2026-10-13)

### Changes

#### Bug Fixes

- fix(matter): make local sensor polling resilient to unreachable sensors ([#490](https://github.com/carlkidcrypto/purpleair_data_logger/issues/490))

#### Build System

- build(deps): Bump the python-dependencies group across 1 directory with 3 updates ([#503](https://github.com/carlkidcrypto/purpleair_data_logger/issues/503))

#### Clarify

- [docs-improvement] Clarify PurpleAirDataLogger docstrings ([#506](https://github.com/carlkidcrypto/purpleair_data_logger/issues/506))

#### Documentation Updates

- docs: clarify validate_sensor_data_before_insert docstring ([#508](https://github.com/carlkidcrypto/purpleair_data_logger/issues/508))
- docs: add versioned documentation for v1.6.0a0 ([#485](https://github.com/carlkidcrypto/purpleair_data_logger/issues/485))

#### Features

- feat: enhance documentation SEO with metadata, OpenGraph, JSON-LD, and overview ([#507](https://github.com/carlkidcrypto/purpleair_data_logger/issues/507))
- feat: use model alias sonnet across all gh-aw workflows ([#504](https://github.com/carlkidcrypto/purpleair_data_logger/issues/504))
- feat: Migrate gh-aw workflows from claude-sonnet-5 to gpt-6.1-sol ([#496](https://github.com/carlkidcrypto/purpleair_data_logger/issues/496))

#### Maintenance

- chore(deps): update Dependabot schedule to weekly ([#505](https://github.com/carlkidcrypto/purpleair_data_logger/issues/505))

---
<a name="v1.6.0a0"></a>
## [v1.6.0a0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.5.0...v1.6.0a0) (2026-09-26)

### Changes

#### Add

- [docs-improvement] add missing docstrings and fix comment typo ([#469](https://github.com/carlkidcrypto/purpleair_data_logger/issues/469))

#### Bug Fixes

- fix(ci): invoke pypa publish directly and extract build-distribution action ([#483](https://github.com/carlkidcrypto/purpleair_data_logger/issues/483))
- fix(ci): scope verify_syntax push to main to avoid duplicate concurrent runs on PRs ([#482](https://github.com/carlkidcrypto/purpleair_data_logger/issues/482))
- fix: handle offline devices gracefully, extract publish action, and bump version to 1.6.0a0 ([#454](https://github.com/carlkidcrypto/purpleair_data_logger/issues/454)) ([#478](https://github.com/carlkidcrypto/purpleair_data_logger/issues/478))

#### Build System

- build(deps): bump purpleair_api from 1.5.0 to 1.5.1a0 ([#484](https://github.com/carlkidcrypto/purpleair_data_logger/issues/484))
- build(deps): Bump coverage from 7.16.0 to 7.16.1 ([#471](https://github.com/carlkidcrypto/purpleair_data_logger/issues/471))
- build(deps): Bump coverage from 7.16.0 to 7.16.1 in /tests ([#472](https://github.com/carlkidcrypto/purpleair_data_logger/issues/472))
- build(deps): Bump coverage from 7.15.3 to 7.16.0 ([#460](https://github.com/carlkidcrypto/purpleair_data_logger/issues/460))
- build(deps): Bump coverage from 7.15.3 to 7.16.0 in /tests ([#461](https://github.com/carlkidcrypto/purpleair_data_logger/issues/461))
- build(deps): Bump peter-evans/create-pull-request from 7 to 8 ([#437](https://github.com/carlkidcrypto/purpleair_data_logger/issues/437))
- build(deps): Bump actions/deploy-pages from 4 to 5 ([#435](https://github.com/carlkidcrypto/purpleair_data_logger/issues/435))
- build(deps): Bump actions/upload-pages-artifact from 4 to 5 ([#434](https://github.com/carlkidcrypto/purpleair_data_logger/issues/434))
- build(deps): Bump actions/cache from 4 to 6 ([#436](https://github.com/carlkidcrypto/purpleair_data_logger/issues/436))

#### Continuous Integration

- ci: remove codeql.yml as repo uses GitHub default CodeQL setup ([#477](https://github.com/carlkidcrypto/purpleair_data_logger/issues/477))

#### Documentation Updates

- docs: fix small typos in README and PSQL logger docstring ([#467](https://github.com/carlkidcrypto/purpleair_data_logger/issues/467))
- docs: add versioned documentation for v1.5.0 ([#441](https://github.com/carlkidcrypto/purpleair_data_logger/issues/441))

#### Features

- feat(ci): backport workflow optimizations, AIC limits, and helper scripts from ezsnmp ([#475](https://github.com/carlkidcrypto/purpleair_data_logger/issues/475))

#### GH

- GH AW ([#466](https://github.com/carlkidcrypto/purpleair_data_logger/issues/466))

#### Maintenance

- chore(docs): update changelog ([#453](https://github.com/carlkidcrypto/purpleair_data_logger/issues/453))

#### Refresh

- Refresh GH-AW container pins in lockfiles ([#443](https://github.com/carlkidcrypto/purpleair_data_logger/issues/443))

#### Tests

- test: cover PurpleAirMatterDataLogger._start_http_server ([#468](https://github.com/carlkidcrypto/purpleair_data_logger/issues/468))

---
<a name="v1.5.0"></a>
## [v1.5.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.5.0a2...v1.5.0) (2026-08-11)

### Changes

#### Additions

- [coverage-autofix] Add tests to raise PurpleAirMatterDataLogger coverage to 99% ([#429](https://github.com/carlkidcrypto/purpleair_data_logger/issues/429))

#### Build System

- build(deps): Bump coverage from 7.15.2 to 7.15.3 in /tests ([#427](https://github.com/carlkidcrypto/purpleair_data_logger/issues/427))
- build(deps): Bump coverage from 7.15.2 to 7.15.3 ([#424](https://github.com/carlkidcrypto/purpleair_data_logger/issues/424))
- build(deps): Bump actions/checkout from 6 to 7 ([#413](https://github.com/carlkidcrypto/purpleair_data_logger/issues/413))

#### Documentation Updates

- docs: fix typos and grammar in README, JSONToMatterBridge, and helper comment ([#440](https://github.com/carlkidcrypto/purpleair_data_logger/issues/440))
- docs: fix duplicated word typo in inline comments ([#430](https://github.com/carlkidcrypto/purpleair_data_logger/issues/430))
- docs: fix incorrect Air Quality Sensor device type ID in JSONToMatterBridge.rst ([#428](https://github.com/carlkidcrypto/purpleair_data_logger/issues/428))

#### Feature

- Feature/prep for new release ([#438](https://github.com/carlkidcrypto/purpleair_data_logger/issues/438))
- Feature/revamp sphinx ([#433](https://github.com/carlkidcrypto/purpleair_data_logger/issues/433))

#### Maintenance

- chore(docs): update changelog ([#439](https://github.com/carlkidcrypto/purpleair_data_logger/issues/439))

---
<a name="v1.5.0a2"></a>
## [v1.5.0a2](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.5.0a1...v1.5.0a2) (2026-08-05)

### Changes

#### Documentation Updates

- docs: fix typos and grammar in README, JSONToMatterBridge, and helper comment ([#420](https://github.com/carlkidcrypto/purpleair_data_logger/issues/420))

#### Feature

- Feature/move matterbridge ([#422](https://github.com/carlkidcrypto/purpleair_data_logger/issues/422))
- Feature/matter data logger 3 ([#418](https://github.com/carlkidcrypto/purpleair_data_logger/issues/418))
- Feature/matter data logger 2 ([#417](https://github.com/carlkidcrypto/purpleair_data_logger/issues/417))
- Feature/matter data logger ([#321](https://github.com/carlkidcrypto/purpleair_data_logger/issues/321))

#### Maintenance

- chore(docs): update changelog ([#419](https://github.com/carlkidcrypto/purpleair_data_logger/issues/419))

#### Make

- Make new Docs ([#410](https://github.com/carlkidcrypto/purpleair_data_logger/issues/410))

---
<a name="v1.5.0a1"></a>
## [v1.5.0a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.5.0a0...v1.5.0a1) (2026-08-01)

### Changes

#### Bug Fixes

- [docs-improvement] Fix typos, grammar, and inaccurate inline comments ([#405](https://github.com/carlkidcrypto/purpleair_data_logger/issues/405))
- [docs-improvement] Fix README badge table format ([#399](https://github.com/carlkidcrypto/purpleair_data_logger/issues/399))
- Fix documentation typos and docstrings ([#387](https://github.com/carlkidcrypto/purpleair_data_logger/issues/387))
- Fix: add copilot-requests permission to all agentic workflows and re-compile ([#376](https://github.com/carlkidcrypto/purpleair_data_logger/issues/376))

#### Build System

- build(deps): Bump coverage from 7.15.0 to 7.15.2 ([#385](https://github.com/carlkidcrypto/purpleair_data_logger/issues/385))
- build(deps): Bump coverage from 7.15.0 to 7.15.2 in /tests ([#386](https://github.com/carlkidcrypto/purpleair_data_logger/issues/386))
- build(deps): Bump actions/setup-python from 6 to 7 ([#390](https://github.com/carlkidcrypto/purpleair_data_logger/issues/390))
- build(deps): Bump prometheus-client from 0.25.0 to 0.26.0 ([#395](https://github.com/carlkidcrypto/purpleair_data_logger/issues/395))
- build(deps): Bump prometheus-client from 0.25.0 to 0.26.0 in /tests ([#396](https://github.com/carlkidcrypto/purpleair_data_logger/issues/396))
- build(deps): Bump coverage from 7.14.3 to 7.15.0 in /tests ([#370](https://github.com/carlkidcrypto/purpleair_data_logger/issues/370))
- build(deps): Bump coverage from 7.14.3 to 7.15.0 ([#369](https://github.com/carlkidcrypto/purpleair_data_logger/issues/369))
- build(deps): Bump coverage from 7.14.2 to 7.14.3 ([#356](https://github.com/carlkidcrypto/purpleair_data_logger/issues/356))
- build(deps): Bump carlkidcrypto/os-specific-runner from 2.3.0 to 2.3.1 ([#355](https://github.com/carlkidcrypto/purpleair_data_logger/issues/355))
- build(deps): Bump github/gh-aw-actions/setup from 0.77.5 to 0.81.3 ([#360](https://github.com/carlkidcrypto/purpleair_data_logger/issues/360))

#### Coverage

- coverage: add pragma no cover to __main__ entry point in PurpleAirPrometheusDataLogger ([#352](https://github.com/carlkidcrypto/purpleair_data_logger/issues/352))

#### Dependency Updates

- Bump Versions ([#408](https://github.com/carlkidcrypto/purpleair_data_logger/issues/408))
- Bump coverage from 7.14.1 to 7.14.2 in /tests ([#354](https://github.com/carlkidcrypto/purpleair_data_logger/issues/354))
- Bump coverage from 7.14.1 to 7.14.2 ([#353](https://github.com/carlkidcrypto/purpleair_data_logger/issues/353))
- Bump actions/checkout from 6 to 7 ([#351](https://github.com/carlkidcrypto/purpleair_data_logger/issues/351))
- Bump codecov/codecov-action from 6 to 7 ([#344](https://github.com/carlkidcrypto/purpleair_data_logger/issues/344))

#### Documentation Updates

- docs: fix typos, grammar, and docstring inaccuracies ([#358](https://github.com/carlkidcrypto/purpleair_data_logger/issues/358))
- docs: fix typos, docstring gaps, and clarify NULL vs None ([#350](https://github.com/carlkidcrypto/purpleair_data_logger/issues/350))
- docs: fix typos, docstring gaps, and add missing Sphinx RST files ([#348](https://github.com/carlkidcrypto/purpleair_data_logger/issues/348))
- docs: fix typos, grammar, and add missing Loki/Prometheus usage sections ([#346](https://github.com/carlkidcrypto/purpleair_data_logger/issues/346))

#### Feature

- Feature/update gh aw 2 ([#407](https://github.com/carlkidcrypto/purpleair_data_logger/issues/407))

#### GH

- GH AW ([#406](https://github.com/carlkidcrypto/purpleair_data_logger/issues/406))

#### Improve

- Improve docs clarity and prevent stale workflow branch failures ([#404](https://github.com/carlkidcrypto/purpleair_data_logger/issues/404))

#### Re

- Re‑compile workflows to resolve lock file mismatch (issue [#339](https://github.com/carlkidcrypto/purpleair_data_logger/issues/339)) ([#340](https://github.com/carlkidcrypto/purpleair_data_logger/issues/340))

#### Standardize

- Standardize agentic workflows on supported Copilot model ([#338](https://github.com/carlkidcrypto/purpleair_data_logger/issues/338))

#### Updates

- Update dependabot.yml ([#345](https://github.com/carlkidcrypto/purpleair_data_logger/issues/345))

---
<a name="v1.5.0a0"></a>
## [v1.5.0a0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.4.2...v1.5.0a0) (2026-06-05)

### Changes

#### Additions

- Add Buy Me a Coffee username for sponsorship ([#252](https://github.com/carlkidcrypto/purpleair_data_logger/issues/252))

#### Bug Fixes

- fix: resolve workflow 0-jobs failure on push triggers ([#303](https://github.com/carlkidcrypto/purpleair_data_logger/issues/303))
- fix: add workflows write permission to recompile_agentic_workflows.yml ([#302](https://github.com/carlkidcrypto/purpleair_data_logger/issues/302))
- fix: correct workflow action versions and invalid permission scope ([#300](https://github.com/carlkidcrypto/purpleair_data_logger/issues/300))
- fix: exclude main branch at trigger level to prevent 0-jobs failure ([#299](https://github.com/carlkidcrypto/purpleair_data_logger/issues/299))
- fix: recompile workflow skip via job-level if + allow dependabot to update agentic workflow files ([#297](https://github.com/carlkidcrypto/purpleair_data_logger/issues/297))
- fix: sync coverage_autofix_every_3_days.lock.yml frontmatter hash ([#293](https://github.com/carlkidcrypto/purpleair_data_logger/issues/293))

#### Bug Fixes

- Fix agentic workflow engine failure caused by gh-aw-actions version mismatch ([#294](https://github.com/carlkidcrypto/purpleair_data_logger/issues/294))
- Fix Coverage Autofix workflow: configure allowed-base-branches for create_pull_request ([#282](https://github.com/carlkidcrypto/purpleair_data_logger/issues/282))
- [docs-improvement] Fix typos, grammar errors, and misleading docstrings ([#280](https://github.com/carlkidcrypto/purpleair_data_logger/issues/280))
- Fix docs CI workflow: allow PR creation targeting main branch ([#274](https://github.com/carlkidcrypto/purpleair_data_logger/issues/274))
- [docs-improvement] Fix docstring and comment errors across data logger modules ([#264](https://github.com/carlkidcrypto/purpleair_data_logger/issues/264))

#### Compile

- Compile agentic workflow markdown files to `.lock.yml` using gh-aw ([#257](https://github.com/carlkidcrypto/purpleair_data_logger/issues/257))

#### Copilot

- Copilot/fix syntax issues ([#334](https://github.com/carlkidcrypto/purpleair_data_logger/issues/334))

#### Dependency Updates

- Bump To 1.5.0a0 ([#336](https://github.com/carlkidcrypto/purpleair_data_logger/issues/336))
- Bump github/gh-aw-actions from 0.77.5 to 0.78.1 ([#333](https://github.com/carlkidcrypto/purpleair_data_logger/issues/333))
- Bump github/gh-aw-actions from 0.77.5 to 0.78.1 ([#329](https://github.com/carlkidcrypto/purpleair_data_logger/issues/329))
- Bump github/gh-aw-actions from 0.77.1 to 0.77.5 ([#328](https://github.com/carlkidcrypto/purpleair_data_logger/issues/328))
- Bump github/gh-aw-actions from 0.75.4 to 0.77.1 ([#327](https://github.com/carlkidcrypto/purpleair_data_logger/issues/327))
- Bump coverage from 7.14.0 to 7.14.1 ([#323](https://github.com/carlkidcrypto/purpleair_data_logger/issues/323))
- Bump coverage from 7.14.0 to 7.14.1 in /tests ([#324](https://github.com/carlkidcrypto/purpleair_data_logger/issues/324))
- Bump psf/black from 26.5.0 to 26.5.1 ([#316](https://github.com/carlkidcrypto/purpleair_data_logger/issues/316))
- Bump black from 26.5.0 to 26.5.1 ([#317](https://github.com/carlkidcrypto/purpleair_data_logger/issues/317))
- Bump github/gh-aw-actions from 0.74.4 to 0.75.4 ([#320](https://github.com/carlkidcrypto/purpleair_data_logger/issues/320))
- Bump github/gh-aw-actions from 0.71.3 to 0.74.4 ([#313](https://github.com/carlkidcrypto/purpleair_data_logger/issues/313))
- Bump psf/black from 26.3.1 to 26.5.0 ([#314](https://github.com/carlkidcrypto/purpleair_data_logger/issues/314))
- Bump black from 26.3.1 to 26.5.0 ([#315](https://github.com/carlkidcrypto/purpleair_data_logger/issues/315))
- Bump github/gh-aw-actions from 0.71.1 to 0.71.3 ([#298](https://github.com/carlkidcrypto/purpleair_data_logger/issues/298))
- Bump coverage from 7.13.5 to 7.14.0 ([#308](https://github.com/carlkidcrypto/purpleair_data_logger/issues/308))
- Bump coverage from 7.13.5 to 7.14.0 in /tests ([#309](https://github.com/carlkidcrypto/purpleair_data_logger/issues/309))
- Bump actions/checkout from 4 to 6 ([#306](https://github.com/carlkidcrypto/purpleair_data_logger/issues/306))
- Bump actions/github-script ([#295](https://github.com/carlkidcrypto/purpleair_data_logger/issues/295))
- Bump actions/checkout from 4 to 6 ([#296](https://github.com/carlkidcrypto/purpleair_data_logger/issues/296))
- Bump github/gh-aw-actions from 0.71.2 to 0.71.3 ([#290](https://github.com/carlkidcrypto/purpleair_data_logger/issues/290))
- Bump github/gh-aw-actions from 0.71.0 to 0.71.2 ([#289](https://github.com/carlkidcrypto/purpleair_data_logger/issues/289))
- Bump actions/github-script ([#276](https://github.com/carlkidcrypto/purpleair_data_logger/issues/276))
- Bump carlkidcrypto/os-specific-runner from 2.2.0 to 2.3.0 ([#279](https://github.com/carlkidcrypto/purpleair_data_logger/issues/279))
- Bump github/gh-aw-actions from 0.69.3 to 0.71.0 ([#278](https://github.com/carlkidcrypto/purpleair_data_logger/issues/278))
- Bump github/gh-aw-actions from 0.68.3 to 0.69.3 ([#277](https://github.com/carlkidcrypto/purpleair_data_logger/issues/277))
- Bump github/gh-aw-actions from 0.69.0 to 0.69.3 ([#275](https://github.com/carlkidcrypto/purpleair_data_logger/issues/275))
- Bump tj-actions/changed-files from 47.0.5 to 47.0.6 ([#270](https://github.com/carlkidcrypto/purpleair_data_logger/issues/270))
- Bump github/gh-aw-actions from 0.68.3 to 0.69.0 ([#272](https://github.com/carlkidcrypto/purpleair_data_logger/issues/272))
- Bump github/gh-aw-actions from 0.68.2 to 0.68.3 ([#265](https://github.com/carlkidcrypto/purpleair_data_logger/issues/265))
- Bump pypa/gh-action-pypi-publish[@release](https://github.com/release)/v1.13 from 1.13 to 1.14 ([#256](https://github.com/carlkidcrypto/purpleair_data_logger/issues/256))
- Bump actions/github-script from 8.0.0 to 9.0.0 ([#259](https://github.com/carlkidcrypto/purpleair_data_logger/issues/259))
- Bump github/gh-aw-actions from 0.68.0 to 0.68.2 ([#262](https://github.com/carlkidcrypto/purpleair_data_logger/issues/262))
- Bump coverage from 7.13.4 to 7.13.5 ([#253](https://github.com/carlkidcrypto/purpleair_data_logger/issues/253))
- Bump codecov/codecov-action from 5 to 6 ([#254](https://github.com/carlkidcrypto/purpleair_data_logger/issues/254))
- Bump black from 26.1.0 to 26.3.1 in the pip group across 1 directory ([#250](https://github.com/carlkidcrypto/purpleair_data_logger/issues/250))
- Bump psf/black from 26.3.0 to 26.3.1 ([#251](https://github.com/carlkidcrypto/purpleair_data_logger/issues/251))
- Bump black from 26.1.0 to 26.3.0 ([#249](https://github.com/carlkidcrypto/purpleair_data_logger/issues/249))

#### Documentation Updates

- docs: complete incomplete constant comments, fix class docstrings, remove stale inline comments ([#269](https://github.com/carlkidcrypto/purpleair_data_logger/issues/269))
- docs: fix typos, capitalization, and broken error messages in docs and docstrings ([#266](https://github.com/carlkidcrypto/purpleair_data_logger/issues/266))

#### Features

- feat: add Python Version Watcher agentic workflow + flow manager gh-aw docs ([#301](https://github.com/carlkidcrypto/purpleair_data_logger/issues/301))
- feat: add Prometheus storage backend for PurpleAir data logger ([#283](https://github.com/carlkidcrypto/purpleair_data_logger/issues/283))
- feat: add Grafana Loki storage backend ([#286](https://github.com/carlkidcrypto/purpleair_data_logger/issues/286))
- feat: add agentic workflow instruction files adapted from ezsnmp ([#255](https://github.com/carlkidcrypto/purpleair_data_logger/issues/255))

#### Recompile

- Recompile Agnetic Workflows ([#335](https://github.com/carlkidcrypto/purpleair_data_logger/issues/335))
- Recompile Agnetic workflow ([#331](https://github.com/carlkidcrypto/purpleair_data_logger/issues/331))

#### Remove

- Remove behave tests and all associated infrastructure ([#284](https://github.com/carlkidcrypto/purpleair_data_logger/issues/284))

#### Tests

- [coverage-autofix] tests: improve coverage from 84% to 100% ([#263](https://github.com/carlkidcrypto/purpleair_data_logger/issues/263))

---
<a name="v1.4.2"></a>
## [v1.4.2](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.4.1...v1.4.2) (2026-03-08)

### Changes

#### Bug Fixes

- Fix Black formatting failures on 3 Python files ([#246](https://github.com/carlkidcrypto/purpleair_data_logger/issues/246))

#### Dependency Updates

- Bump carlkidcrypto/os-specific-runner from 2.1.3 to 2.2.0 ([#247](https://github.com/carlkidcrypto/purpleair_data_logger/issues/247))
- Bump psf/black ([#248](https://github.com/carlkidcrypto/purpleair_data_logger/issues/248))
- Bump tj-actions/changed-files from 47.0.4 to 47.0.5 ([#245](https://github.com/carlkidcrypto/purpleair_data_logger/issues/245))
- Bump purpleair-api from 1.3.0 to 1.4.0 ([#244](https://github.com/carlkidcrypto/purpleair_data_logger/issues/244))
- Bump tj-actions/changed-files from 47.0.2 to 47.0.4 ([#241](https://github.com/carlkidcrypto/purpleair_data_logger/issues/241))
- Bump actions/upload-artifact from 6 to 7 ([#242](https://github.com/carlkidcrypto/purpleair_data_logger/issues/242))
- Bump actions/download-artifact from 7 to 8 ([#243](https://github.com/carlkidcrypto/purpleair_data_logger/issues/243))

---
<a name="v1.4.1"></a>
## [v1.4.1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.4.0...v1.4.1) (2026-02-16)

### Changes

#### Additions

- Add environment fields to PyPI trusted publisher workflows ([#240](https://github.com/carlkidcrypto/purpleair_data_logger/issues/240))

#### Dependency Updates

- Bump tj-actions/changed-files from 47.0.1 to 47.0.2 ([#237](https://github.com/carlkidcrypto/purpleair_data_logger/issues/237))
- Bump coverage from 7.13.2 to 7.13.4 ([#238](https://github.com/carlkidcrypto/purpleair_data_logger/issues/238))
- Bump sphinx from 8.2.3 to 9.1.0 ([#231](https://github.com/carlkidcrypto/purpleair_data_logger/issues/231))
- Bump actions/upload-artifact from 5 to 6 ([#229](https://github.com/carlkidcrypto/purpleair_data_logger/issues/229))
- Bump actions/download-artifact from 6 to 7 ([#228](https://github.com/carlkidcrypto/purpleair_data_logger/issues/228))
- Bump actions/checkout from 5 to 6 ([#219](https://github.com/carlkidcrypto/purpleair_data_logger/issues/219))
- Bump tj-actions/changed-files from 47.0.0 to 47.0.1 ([#227](https://github.com/carlkidcrypto/purpleair_data_logger/issues/227))
- Bump coverage from 7.11.0 to 7.13.2 ([#235](https://github.com/carlkidcrypto/purpleair_data_logger/issues/235))
- Bump sphinx-rtd-theme from 3.0.2 to 3.1.0 ([#232](https://github.com/carlkidcrypto/purpleair_data_logger/issues/232))
- Bump psf/black from 25.11.0 to 26.1.0 ([#233](https://github.com/carlkidcrypto/purpleair_data_logger/issues/233))
- Bump black from 25.9.0 to 26.1.0 ([#234](https://github.com/carlkidcrypto/purpleair_data_logger/issues/234))
- Bump psf/black from 25.9.0 to 25.11.0 ([#215](https://github.com/carlkidcrypto/purpleair_data_logger/issues/215))
- Bump actions/download-artifact from 4 to 6 ([#212](https://github.com/carlkidcrypto/purpleair_data_logger/issues/212))
- Bump carlkidcrypto/os-specific-runner from 2.1.1 to 2.1.3 ([#211](https://github.com/carlkidcrypto/purpleair_data_logger/issues/211))
- Bump actions/checkout from 4 to 5 ([#210](https://github.com/carlkidcrypto/purpleair_data_logger/issues/210))
- Bump actions/upload-artifact from 4 to 5 ([#209](https://github.com/carlkidcrypto/purpleair_data_logger/issues/209))
- Bump actions/setup-python from 5 to 6 ([#213](https://github.com/carlkidcrypto/purpleair_data_logger/issues/213))
- Bump pg8000 from 1.31.4 to 1.31.5 ([#199](https://github.com/carlkidcrypto/purpleair_data_logger/issues/199))
- Bump coverage from 7.9.0 to 7.11.0 ([#201](https://github.com/carlkidcrypto/purpleair_data_logger/issues/201))
- Bump behave from 1.2.6 to 1.3.3 ([#198](https://github.com/carlkidcrypto/purpleair_data_logger/issues/198))
- Bump pg8000 from 1.31.2 to 1.31.4 ([#187](https://github.com/carlkidcrypto/purpleair_data_logger/issues/187))
- Bump coverage from 7.8.0 to 7.9.0 ([#184](https://github.com/carlkidcrypto/purpleair_data_logger/issues/184))
- Bump tj-actions/changed-files ([#181](https://github.com/carlkidcrypto/purpleair_data_logger/issues/181))
- Bump coverage from 7.6.12 to 7.8.0 ([#180](https://github.com/carlkidcrypto/purpleair_data_logger/issues/180))
- Bump sphinx from 8.1.3 to 8.2.3 ([#177](https://github.com/carlkidcrypto/purpleair_data_logger/issues/177))
- Bump coverage from 7.6.10 to 7.6.12 ([#174](https://github.com/carlkidcrypto/purpleair_data_logger/issues/174))
- Bump purpleair-api from 1.2.0 to 1.3.0 ([#172](https://github.com/carlkidcrypto/purpleair_data_logger/issues/172))

#### Migrate

- Migrate PyPI publishing workflows to Trusted Publisher authentication ([#239](https://github.com/carlkidcrypto/purpleair_data_logger/issues/239))

#### Potential

- Potential fix for code scanning alert no. 10: Workflow does not contain permissions ([#207](https://github.com/carlkidcrypto/purpleair_data_logger/issues/207))
- Potential fix for code scanning alert no. 9: Workflow does not contain permissions ([#206](https://github.com/carlkidcrypto/purpleair_data_logger/issues/206))
- Potential fix for code scanning alert no. 5: Workflow does not contain permissions ([#205](https://github.com/carlkidcrypto/purpleair_data_logger/issues/205))
- Potential fix for code scanning alert no. 4: Workflow does not contain permissions ([#204](https://github.com/carlkidcrypto/purpleair_data_logger/issues/204))
- Potential fix for code scanning alert no. 3: Workflow does not contain permissions ([#203](https://github.com/carlkidcrypto/purpleair_data_logger/issues/203))
- Potential fix for code scanning alert no. 2: Workflow does not contain permissions ([#202](https://github.com/carlkidcrypto/purpleair_data_logger/issues/202))

#### Releases

- Release/prep for release 1.4.1 ([#208](https://github.com/carlkidcrypto/purpleair_data_logger/issues/208))

#### Updates

- Update dependabot.yml ([#214](https://github.com/carlkidcrypto/purpleair_data_logger/issues/214))

---
<a name="v1.4.0"></a>
## [v1.4.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.3...v1.4.0) (2025-01-08)

### Changes

#### Dependency Updates

- Bump coverage from 7.6.9 to 7.6.10 ([#170](https://github.com/carlkidcrypto/purpleair_data_logger/issues/170))
- Bump coverage from 7.6.7 to 7.6.9 ([#168](https://github.com/carlkidcrypto/purpleair_data_logger/issues/168))
- Bump tj-actions/changed-files from 45.0.4 to 45.0.5 ([#169](https://github.com/carlkidcrypto/purpleair_data_logger/issues/169))
- Bump coverage from 7.6.5 to 7.6.7 ([#166](https://github.com/carlkidcrypto/purpleair_data_logger/issues/166))
- Bump sphinx-rtd-theme from 3.0.1 to 3.0.2 ([#163](https://github.com/carlkidcrypto/purpleair_data_logger/issues/163))
- Bump coverage from 7.6.4 to 7.6.5 ([#164](https://github.com/carlkidcrypto/purpleair_data_logger/issues/164))
- Bump codecov/codecov-action from 4 to 5 ([#165](https://github.com/carlkidcrypto/purpleair_data_logger/issues/165))
- Bump tj-actions/changed-files from 45.0.3 to 45.0.4 ([#162](https://github.com/carlkidcrypto/purpleair_data_logger/issues/162))
- Bump sphinx from 8.0.2 to 8.1.3 ([#159](https://github.com/carlkidcrypto/purpleair_data_logger/issues/159))
- Bump coverage from 7.6.2 to 7.6.4 ([#161](https://github.com/carlkidcrypto/purpleair_data_logger/issues/161))
- Bump psf/black from 24.8.0 to 24.10.0 ([#155](https://github.com/carlkidcrypto/purpleair_data_logger/issues/155))
- Bump sphinx-rtd-theme from 3.0.0rc4 to 3.0.1 ([#156](https://github.com/carlkidcrypto/purpleair_data_logger/issues/156))
- Bump coverage from 7.6.1 to 7.6.2 ([#157](https://github.com/carlkidcrypto/purpleair_data_logger/issues/157))
- Bump tj-actions/changed-files from 45.0.2 to 45.0.3 ([#153](https://github.com/carlkidcrypto/purpleair_data_logger/issues/153))
- Bump purpleair-api from 1.2.0a2 to 1.2.0 ([#149](https://github.com/carlkidcrypto/purpleair_data_logger/issues/149))
- Bump carlkidcrypto/os-specific-runner from 2.1.0 to 2.1.1 ([#151](https://github.com/carlkidcrypto/purpleair_data_logger/issues/151))
- Bump sphinx-rtd-theme from 3.0.0rc2 to 3.0.0rc4 ([#152](https://github.com/carlkidcrypto/purpleair_data_logger/issues/152))
- Bump dep ([#148](https://github.com/carlkidcrypto/purpleair_data_logger/issues/148))
- Bump tj-actions/changed-files from 45.0.1 to 45.0.2 ([#146](https://github.com/carlkidcrypto/purpleair_data_logger/issues/146))
- Bump tj-actions/changed-files from 45.0.0 to 45.0.1 ([#145](https://github.com/carlkidcrypto/purpleair_data_logger/issues/145))
- Bump tj-actions/changed-files from 44.5.7 to 45.0.0 ([#144](https://github.com/carlkidcrypto/purpleair_data_logger/issues/144))
- Bump sphinx from 7.4.7 to 8.0.2 ([#140](https://github.com/carlkidcrypto/purpleair_data_logger/issues/140))
- Bump psf/black from 24.4.2 to 24.8.0 ([#142](https://github.com/carlkidcrypto/purpleair_data_logger/issues/142))
- Bump coverage from 7.6.0 to 7.6.1 ([#143](https://github.com/carlkidcrypto/purpleair_data_logger/issues/143))
- Bump tj-actions/changed-files from 44.5.6 to 44.5.7 ([#141](https://github.com/carlkidcrypto/purpleair_data_logger/issues/141))
- Bump sphinx from 7.4.6 to 7.4.7 ([#139](https://github.com/carlkidcrypto/purpleair_data_logger/issues/139))
- Bump tj-actions/changed-files from 44.5.5 to 44.5.6 ([#138](https://github.com/carlkidcrypto/purpleair_data_logger/issues/138))
- Bump sphinx from 7.4.5 to 7.4.6 ([#137](https://github.com/carlkidcrypto/purpleair_data_logger/issues/137))
- Bump coverage from 7.5.4 to 7.6.0 ([#134](https://github.com/carlkidcrypto/purpleair_data_logger/issues/134))
- Bump sphinx from 7.3.7 to 7.4.5 ([#136](https://github.com/carlkidcrypto/purpleair_data_logger/issues/136))
- Bump tj-actions/changed-files from 44.5.4 to 44.5.5 ([#133](https://github.com/carlkidcrypto/purpleair_data_logger/issues/133))
- Bump tj-actions/changed-files from 44.5.1 to 44.5.4 ([#132](https://github.com/carlkidcrypto/purpleair_data_logger/issues/132))
- Bump coverage from 7.5.3 to 7.5.4 ([#131](https://github.com/carlkidcrypto/purpleair_data_logger/issues/131))
- Bump tj-actions/changed-files from 44.5.0 to 44.5.1 ([#126](https://github.com/carlkidcrypto/purpleair_data_logger/issues/126))
- Bump coverage from 7.5.1 to 7.5.3 ([#128](https://github.com/carlkidcrypto/purpleair_data_logger/issues/128))
- Bump tj-actions/changed-files from 44.3.0 to 44.4.0 ([#124](https://github.com/carlkidcrypto/purpleair_data_logger/issues/124))
- Bump coverage from 7.5.0 to 7.5.1 ([#123](https://github.com/carlkidcrypto/purpleair_data_logger/issues/123))
- Bump carlkidcrypto/os-specific-runner from 2.0.0 to 2.1.0 ([#122](https://github.com/carlkidcrypto/purpleair_data_logger/issues/122))
- Bump pg8000 from 1.31.1 to 1.31.2 ([#121](https://github.com/carlkidcrypto/purpleair_data_logger/issues/121))
- Bump coverage from 7.4.4 to 7.5.0 ([#118](https://github.com/carlkidcrypto/purpleair_data_logger/issues/118))
- Bump psf/black from 24.4.0 to 24.4.2 ([#120](https://github.com/carlkidcrypto/purpleair_data_logger/issues/120))
- Bump sphinx from 7.3.6 to 7.3.7 ([#117](https://github.com/carlkidcrypto/purpleair_data_logger/issues/117))
- Bump tj-actions/changed-files from 44.1.0 to 44.3.0 ([#116](https://github.com/carlkidcrypto/purpleair_data_logger/issues/116))
- Bump tj-actions/changed-files from 44.0.1 to 44.1.0 ([#115](https://github.com/carlkidcrypto/purpleair_data_logger/issues/115))
- Bump sphinx from 7.3.4 to 7.3.6 ([#114](https://github.com/carlkidcrypto/purpleair_data_logger/issues/114))
- Bump sphinx from 7.2.6 to 7.3.4 ([#113](https://github.com/carlkidcrypto/purpleair_data_logger/issues/113))
- Bump psf/black from 24.3.0 to 24.4.0 ([#112](https://github.com/carlkidcrypto/purpleair_data_logger/issues/112))
- Bump tj-actions/changed-files from 44.0.0 to 44.0.1 ([#111](https://github.com/carlkidcrypto/purpleair_data_logger/issues/111))
- Bump pg8000 from 1.31.0 to 1.31.1 ([#110](https://github.com/carlkidcrypto/purpleair_data_logger/issues/110))
- Bump requests-mock from 1.12.0 to 1.12.1 ([#109](https://github.com/carlkidcrypto/purpleair_data_logger/issues/109))
- Bump pg8000 from 1.30.5 to 1.31.0 ([#108](https://github.com/carlkidcrypto/purpleair_data_logger/issues/108))
- Bump requests-mock from 1.11.0 to 1.12.0 ([#107](https://github.com/carlkidcrypto/purpleair_data_logger/issues/107))
- Bump tj-actions/changed-files from 43.0.1 to 44.0.0 ([#106](https://github.com/carlkidcrypto/purpleair_data_logger/issues/106))
- Bump psf/black from 24.2.0 to 24.3.0 ([#104](https://github.com/carlkidcrypto/purpleair_data_logger/issues/104))
- Bump tj-actions/changed-files from 43.0.0 to 43.0.1 ([#105](https://github.com/carlkidcrypto/purpleair_data_logger/issues/105))
- Bump coverage from 7.4.3 to 7.4.4 ([#103](https://github.com/carlkidcrypto/purpleair_data_logger/issues/103))
- Bump tj-actions/changed-files from 42.1.0 to 43.0.0 ([#102](https://github.com/carlkidcrypto/purpleair_data_logger/issues/102))
- Bump tj-actions/changed-files from 42.0.7 to 42.1.0 ([#101](https://github.com/carlkidcrypto/purpleair_data_logger/issues/101))
- Bump tj-actions/changed-files from 42.0.5 to 42.0.7 ([#100](https://github.com/carlkidcrypto/purpleair_data_logger/issues/100))
- Bump tj-actions/changed-files from 42.0.4 to 42.0.5 ([#98](https://github.com/carlkidcrypto/purpleair_data_logger/issues/98))
- Bump pg8000 from 1.30.4 to 1.30.5 ([#96](https://github.com/carlkidcrypto/purpleair_data_logger/issues/96))
- Bump coverage from 7.4.2 to 7.4.3 ([#97](https://github.com/carlkidcrypto/purpleair_data_logger/issues/97))

#### Drop

- Drop 3.8, Add 3.13 ([#171](https://github.com/carlkidcrypto/purpleair_data_logger/issues/171))

#### Test

- Test New API V1.2.0a1 ([#147](https://github.com/carlkidcrypto/purpleair_data_logger/issues/147))

---
<a name="v1.3.3"></a>
## [v1.3.3](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.2...v1.3.3) (2024-02-21)

### Changes

#### Dependency Updates

- Bump ([#95](https://github.com/carlkidcrypto/purpleair_data_logger/issues/95))
- Bump coverage from 7.4.1 to 7.4.2 ([#94](https://github.com/carlkidcrypto/purpleair_data_logger/issues/94))
- Bump tj-actions/changed-files from 42.0.2 to 42.0.4 ([#93](https://github.com/carlkidcrypto/purpleair_data_logger/issues/93))
- Bump psf/black from 24.1.1 to 24.2.0 ([#92](https://github.com/carlkidcrypto/purpleair_data_logger/issues/92))
- Bump codecov/codecov-action from 3 to 4 ([#91](https://github.com/carlkidcrypto/purpleair_data_logger/issues/91))
- Bump tj-actions/changed-files from 42.0.0 to 42.0.2 ([#88](https://github.com/carlkidcrypto/purpleair_data_logger/issues/88))
- Bump coverage from 7.4.0 to 7.4.1 ([#89](https://github.com/carlkidcrypto/purpleair_data_logger/issues/89))
- Bump psf/black from 23.12.1 to 24.1.1 ([#90](https://github.com/carlkidcrypto/purpleair_data_logger/issues/90))
- Bump tj-actions/changed-files from 41.0.1 to 42.0.0 ([#87](https://github.com/carlkidcrypto/purpleair_data_logger/issues/87))

---
<a name="v1.3.2"></a>
## [v1.3.2](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.1...v1.3.2) (2024-01-05)

### Changes

#### Carlkidcrypto

- carlkidcrypto/os-specific-runner[@v2](https://github.com/v2).0.0 ([#78](https://github.com/carlkidcrypto/purpleair_data_logger/issues/78))

#### Dependency Updates

- Bump purpleair-api from 1.1.2 to 1.1.3 ([#83](https://github.com/carlkidcrypto/purpleair_data_logger/issues/83))
- Bump pg8000 from 1.30.3 to 1.30.4 ([#82](https://github.com/carlkidcrypto/purpleair_data_logger/issues/82))
- Bump coverage from 7.3.4 to 7.4.0 ([#81](https://github.com/carlkidcrypto/purpleair_data_logger/issues/81))
- Bump psf/black from 23.12.0 to 23.12.1 ([#80](https://github.com/carlkidcrypto/purpleair_data_logger/issues/80))
- Bump coverage from 7.3.3 to 7.3.4 ([#79](https://github.com/carlkidcrypto/purpleair_data_logger/issues/79))
- Bump actions/download-artifact from 3 to 4 ([#75](https://github.com/carlkidcrypto/purpleair_data_logger/issues/75))
- Bump actions/upload-artifact from 3 to 4 ([#76](https://github.com/carlkidcrypto/purpleair_data_logger/issues/76))
- Bump coverage from 7.3.2 to 7.3.3 ([#77](https://github.com/carlkidcrypto/purpleair_data_logger/issues/77))

#### Release

- release/v1.3.2 ([#84](https://github.com/carlkidcrypto/purpleair_data_logger/issues/84))

#### Updates

- Update README.md
- Update README.md

---
<a name="v1.3.1"></a>
## [v1.3.1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.0...v1.3.1) (2023-12-12)

### Changes

#### Updates

- Update setup.cfg

---
<a name="v1.3.0"></a>
## [v1.3.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.0a1...v1.3.0) (2023-12-12)

### Changes

#### 66

- 66 update readme ([#67](https://github.com/carlkidcrypto/purpleair_data_logger/issues/67))

#### Create

- Create requirements.txt

#### Dependency Updates

- Bump psf/black from 23.11.0 to 23.12.0 ([#73](https://github.com/carlkidcrypto/purpleair_data_logger/issues/73))
- Bump actions/setup-python from 4 to 5 ([#72](https://github.com/carlkidcrypto/purpleair_data_logger/issues/72))
- Bump sphinx-rtd-theme from 1.3.0 to 2.0.0 ([#70](https://github.com/carlkidcrypto/purpleair_data_logger/issues/70))
- Bump pyhamcrest from 2.0.4 to 2.1.0 ([#69](https://github.com/carlkidcrypto/purpleair_data_logger/issues/69))
- Bump pg8000 from 1.30.1 to 1.30.3 ([#68](https://github.com/carlkidcrypto/purpleair_data_logger/issues/68))

#### Feature

- Feature/move towards setup.cfg ([#71](https://github.com/carlkidcrypto/purpleair_data_logger/issues/71))

#### Prep

- Prep Work ([#74](https://github.com/carlkidcrypto/purpleair_data_logger/issues/74))

#### Sphinx

- Sphinx is caps :(

#### Workflows

- Workflows

---
<a name="v1.3.0a1"></a>
## [v1.3.0a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.3.0a0...v1.3.0a1) (2023-11-23)

### Changes

#### 59

- 59 behave tests improvement ([#65](https://github.com/carlkidcrypto/purpleair_data_logger/issues/65))

---
<a name="v1.3.0a0"></a>
## [v1.3.0a0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.2.1...v1.3.0a0) (2023-11-11)

### Changes

#### 60

- 60 local logging ([#64](https://github.com/carlkidcrypto/purpleair_data_logger/issues/64))

#### Dependency Updates

- Bump psf/black from 23.10.1 to 23.11.0 ([#63](https://github.com/carlkidcrypto/purpleair_data_logger/issues/63))
- Bump psf/black from 23.10.0 to 23.10.1 ([#62](https://github.com/carlkidcrypto/purpleair_data_logger/issues/62))
- Bump psf/black from 23.9.1 to 23.10.0 ([#61](https://github.com/carlkidcrypto/purpleair_data_logger/issues/61))
- Bump psf/black from 23.7.0 to 23.9.1 ([#58](https://github.com/carlkidcrypto/purpleair_data_logger/issues/58))
- Bump actions/checkout from 3 to 4 ([#57](https://github.com/carlkidcrypto/purpleair_data_logger/issues/57))
- Bump psf/black from 23.3.0 to 23.7.0 ([#56](https://github.com/carlkidcrypto/purpleair_data_logger/issues/56))

#### Updates

- Update PurpleAirDataLogger.py

---
<a name="v1.2.1"></a>
## [v1.2.1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.2.1a1...v1.2.1) (2023-06-13)

### Changes

#### V1

- V1.2.1 ([#55](https://github.com/carlkidcrypto/purpleair_data_logger/issues/55))

---
<a name="v1.2.1a1"></a>
## [v1.2.1a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.2.0...v1.2.1a1) (2023-05-17)

### Changes

#### Bugfix

- Bugfix/reducing down mem foot print ([#54](https://github.com/carlkidcrypto/purpleair_data_logger/issues/54))

#### Carlkid1499

- carlkid1499 --> to carlkidcrypto

#### Dependency Updates

- Bump psf/black from 23.1.0 to 23.3.0 ([#53](https://github.com/carlkidcrypto/purpleair_data_logger/issues/53))
- Bump actions/setup-python from 3 to 4 ([#52](https://github.com/carlkidcrypto/purpleair_data_logger/issues/52))

---
<a name="v1.2.0"></a>
## [v1.2.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.2.0a2...v1.2.0) (2023-02-26)

### Changes

#### Feature

- Feature/final prep work for v1.2.0 release ([#51](https://github.com/carlkidcrypto/purpleair_data_logger/issues/51))
- Feature/43 investigate and add sensor groups to data loggers ([#50](https://github.com/carlkidcrypto/purpleair_data_logger/issues/50))

---
<a name="v1.2.0a2"></a>
## [v1.2.0a2](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.2.0a0...v1.2.0a2) (2023-02-18)

### Changes

#### Bugfix

- Bugfix/42 investigate and fix behave tests windows ([#48](https://github.com/carlkidcrypto/purpleair_data_logger/issues/48))

#### Feature

- Feature/35 consider splitting the purpleair python api from the purpleair data loggers ([#49](https://github.com/carlkidcrypto/purpleair_data_logger/issues/49))

---
<a name="v1.2.0a0"></a>
## [v1.2.0a0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.1.0...v1.2.0a0) (2023-02-12)

### Changes

#### Bug

- Bug/40 investigate workflows for pypi ([#45](https://github.com/carlkidcrypto/purpleair_data_logger/issues/45))

#### Bugfix

- Bugfix/40 investigate workflows for pypi try 3 ([#47](https://github.com/carlkidcrypto/purpleair_data_logger/issues/47))
- Bugfix/40 investigate workflows for pypi try 2 ([#46](https://github.com/carlkidcrypto/purpleair_data_logger/issues/46))

#### Feature

- Feature/41 psql data logger continuous aggregates ([#44](https://github.com/carlkidcrypto/purpleair_data_logger/issues/44))

#### Updates

- Update setup.py
- Update build_and_publish_to_test_pypi.yml

#### Workflows

- Workflows

---
<a name="v1.1.0"></a>
## [v1.1.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v1.0.0...v1.1.0) (2023-01-26)

### Changes

#### 25

- 25 Create Happy Path Behave Tests ([#33](https://github.com/carlkidcrypto/purpleair_data_logger/issues/33))

#### Clean

- Clean Up

#### Create

- Create dependabot.yml

#### Debugger

- Debugger and F String

#### Dependency Updates

- Bump actions/upload-artifact from 2 to 3 ([#38](https://github.com/carlkidcrypto/purpleair_data_logger/issues/38))
- Bump actions/download-artifact from 2 to 3 ([#37](https://github.com/carlkidcrypto/purpleair_data_logger/issues/37))

#### Docs

- Docs for [#30](https://github.com/carlkidcrypto/purpleair_data_logger/issues/30)

#### Feature

- Feature/36 create GitHub action for pypi ([#39](https://github.com/carlkidcrypto/purpleair_data_logger/issues/39))
- Feature/31 add support for member api calls ([#34](https://github.com/carlkidcrypto/purpleair_data_logger/issues/34))

#### Fixes

- Fixes

#### New

- New Method

#### Updates

- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py

### Merged Pull Requests

- Merge pull request [#32](https://github.com/carlkidcrypto/purpleair_data_logger/issues/32) from carlkid1499/feature/30-add-support-for-write-keys

---
<a name="v1.0.0"></a>
## [v1.0.0](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.8b1...v1.0.0) (2022-11-10)

### Changes

#### Clean

- Clean Up

#### Create

- Create PurpleAirSQLiteDataLogger.py

#### Doc

- Doc Updates

#### Fixes

- Fixes

#### Grafana

- Grafana Dashboard
- Grafana Dashboard

#### Nearing

- Nearing EOD

#### PSQLDataLogger

- PSQLDataLogger
- PSQLDataLogger Updates

#### Readme

- Readme
- Readme

#### SQLite

- SQLite Data Logger
- SQLite Data Logger

#### Sphinx

- Sphinx Doc

#### Updates

- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirDataLogger.py
- Update issue templates
- Update PurpleAirPSQLQueryStatements.py

### Merged Pull Requests

- Merge pull request [#29](https://github.com/carlkidcrypto/purpleair_data_logger/issues/29) from carlkid1499/feature/documentation_for_v1.0.0_[#24](https://github.com/carlkidcrypto/purpleair_data_logger/issues/24)
- Merge pull request [#28](https://github.com/carlkidcrypto/purpleair_data_logger/issues/28) from carlkid1499/feature/23-create-a-sqlitedatalogger
- Merge pull request [#27](https://github.com/carlkidcrypto/purpleair_data_logger/issues/27) from carlkid1499/feature/continuous_aggregate_issue_[#26](https://github.com/carlkidcrypto/purpleair_data_logger/issues/26)

---
<a name="v0.0.8b1"></a>
## [v0.0.8b1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.7a1...v0.0.8b1) (2022-09-13)

### Changes

#### Base

- Base Class Creation

#### CSV

- CSV Data Logger Work

#### Clean

- Clean Up and New Class

#### Create

- Create settings.json

#### DataLogger

- DataLogger & PSQLStatements

#### Docs

- Docs Again
- Docs

#### Fixes

- Fixes and Custom Error Class

#### Readme

- Readme and Cleanup

#### Sphinx

- Sphinx Docs
- Sphinx Docs

#### Store_sensor_data

- store_sensor_data and static methods

#### Updates

- Update PurpleAirAPI.py
- Update PurpleAirCSVDataLogger.py
- Update PurpleAirCSVDataLoggerConstants.py
- Update settings.json
- Update PurpleAirCSVDataLogger.py

#### Updating

- Updating PurpleAirAPI

### Merged Pull Requests

- Merge pull request [#22](https://github.com/carlkidcrypto/purpleair_data_logger/issues/22) from carlkid1499/feature/update_readme_and_docs_[#18](https://github.com/carlkidcrypto/purpleair_data_logger/issues/18)
- Merge pull request [#21](https://github.com/carlkidcrypto/purpleair_data_logger/issues/21) from carlkid1499/feature/add_historic_sesnor_data_to_PAA_[#16](https://github.com/carlkidcrypto/purpleair_data_logger/issues/16)
- Merge pull request [#20](https://github.com/carlkidcrypto/purpleair_data_logger/issues/20) from carlkid1499/feature/add_basic_csv_logger_[#19](https://github.com/carlkidcrypto/purpleair_data_logger/issues/19)

---
<a name="v0.0.7a1"></a>
## [v0.0.7a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.6a1...v0.0.7a1) (2022-08-22)

### Changes

#### Bug Fixes

- Fix Sample Json

#### Config

- Config File and Docs

#### Dependency Updates

- Bump Version

#### Docs

- Docs

#### New

- New Arg

#### Oops

- Oops, dropped an arg

#### Updates

- Update README.md
- Update PurpleAirPSQLQueryStatements.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLQueryStatements.py

### Merged Pull Requests

- Merge pull request [#14](https://github.com/carlkidcrypto/purpleair_data_logger/issues/14) from carlkid1499/feature/readme_updates_[#11](https://github.com/carlkidcrypto/purpleair_data_logger/issues/11)
- Merge pull request [#13](https://github.com/carlkidcrypto/purpleair_data_logger/issues/13) from carlkid1499/feature/signle_sensor_config_[#9](https://github.com/carlkidcrypto/purpleair_data_logger/issues/9)
- Merge pull request [#12](https://github.com/carlkidcrypto/purpleair_data_logger/issues/12) from carlkid1499/feature/finalize_the_db_[#10](https://github.com/carlkidcrypto/purpleair_data_logger/issues/10)

---
<a name="v0.0.6a1"></a>
## [v0.0.6a1](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.5-alpha...v0.0.6a1) (2022-08-12)

### Changes

#### Adding

- Adding Multiple Sensor Support

#### CML

- CML Entry

#### Checkpoint

- Checkpoint

#### Clean

- Clean Up Work
- Clean Up Main

#### Create

- Create test_config.json

#### Diagrams

- Diagrams

#### Docs

- Docs
- Docs
- Docs and Nones
- Docs Tweak

#### Email

- Email

#### Fixes

- Fixes For gh-pages

#### Just

- Just Doc

#### Module

- Module Fixes

#### Nojekyll

- nojekyll

#### Python

- Python Module Fixes
- Python Modules Fixes

#### Restructure

- Restructure

#### Small

- Small Updates

#### Sphinx

- Sphinx Build

#### Trying

- Trying __init__ again

#### Turning

- Turning Into Python Package

#### Tweaks

- Tweaks to Setup.py

#### Updated

- Updated the Dashboard

#### Updates

- Update setup.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLQueryStatements.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLQueryStatements.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update README.md
- Update PurpleAirAPI.py
- Update PurpleAirAPI.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirAPI.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirPSQLDataLogger.py
- Update PurpleAirAPI.py
- Update __init__.py
- Update PurpleAirPSQLDataLogger.py
- Update setup.py

#### V0

- v0.0.6a

#### Work

- Work towards Multi Sensors

#### Yay

- Yay more doc changes

### Merged Pull Requests

- Merge pull request [#8](https://github.com/carlkidcrypto/purpleair_data_logger/issues/8) from carlkid1499/feature/cleanup_and_optimize
- Merge pull request [#7](https://github.com/carlkidcrypto/purpleair_data_logger/issues/7) from carlkid1499/feature/add_to_pip

---
<a name="v0.0.5-alpha"></a>
## [v0.0.5-alpha](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.4-alpha...v0.0.5-alpha) (2022-07-27)

### Changes

#### Create

- Create PurpleAirAPI (PAA) Data Logger Grafana Dashboard-1658974279769.json

#### New

- New Version of Dashboard

### Merged Pull Requests

- Merge pull request [#6](https://github.com/carlkidcrypto/purpleair_data_logger/issues/6) from carlkid1499/feature/create_grafana_dashboard

---
<a name="v0.0.4-alpha"></a>
## [v0.0.4-alpha](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.3-alpha...v0.0.4-alpha) (2022-07-25)

### Changes

#### Attempt

- Attempt to use TO_TIMESTAMP(

#### Copyrights

- Copyrights and docs

#### Docs

- Docs Yay!

#### Enable

- Enable Storing Of Data

#### Get_multiple_sensors_data

- get_multiple_sensors_data

#### Key

- key Fixes

#### New

- New Method & CONSTS

#### Self

- self.__convert_unix_epoch_timestamp_to_psql_timestamp(
- self.__convert_unix_epoch_timestamp_to_psql_timestamp(

#### Sensor

- Sensor Index

#### TIMESTAMPTZ

- TIMESTAMPTZ

### Reverted Changes

- Attempt to use TO_TIMESTAMP(

### Merged Pull Requests

- Merge pull request [#5](https://github.com/carlkidcrypto/purpleair_data_logger/issues/5) from carlkid1499/feature/updates_to_paa
- Merge pull request [#4](https://github.com/carlkidcrypto/purpleair_data_logger/issues/4) from carlkid1499/feature/use_sphinx_for_auto_docs

---
<a name="v0.0.3-alpha"></a>
## [v0.0.3-alpha](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.2-alpha...v0.0.3-alpha) (2022-07-23)

### Changes

#### Error

- Error Checking

#### Even

- Even more testing

#### HyperTable

- HyperTable Fix

#### Inserting

- Inserting Data

#### Inserts

- Inserts

#### Last

- Last of Insert Queries

#### Miscellaneous_fields

- miscellaneous_fields

#### Modified

- Modified sensor data

#### More

- More Testing

#### Pm1_0_fields

- pm1_0_fields

#### Tests

- test

### Merged Pull Requests

- Merge pull request [#3](https://github.com/carlkidcrypto/purpleair_data_logger/issues/3) from carlkid1499/feature/enable_storing_of_data

---
<a name="v0.0.2-alpha"></a>
## [v0.0.2-alpha](https://github.com/carlkidcrypto/purpleair_data_logger/compare/v0.0.1-alpha...v0.0.2-alpha) (2022-07-23)

### Changes

#### Basic

- Basic PAA Data Logger

#### Column

- Column Data Types Fix

#### DB

- DB Fixs.....

#### Database

- Database Fix
- Database

#### Even

- Even More Database Fixes

#### GitIgnore

- GitIgnore

#### Small

- Small Fix

#### Table

- Table Data Types

### Merged Pull Requests

- Merge pull request [#2](https://github.com/carlkidcrypto/purpleair_data_logger/issues/2) from carlkid1499/feature/create_basic_data_logger

---
<a name="v0.0.1-alpha"></a>
## v0.0.1-alpha (2022-07-20)

### Changes

#### Initial Commits

- Initial commit

#### More

- More Methods

#### V0

- V0.0.1a

#### __check_an_api_key

- __check_an_api_key

### Merged Pull Requests

- Merge pull request [#1](https://github.com/carlkidcrypto/purpleair_data_logger/issues/1) from carlkid1499/feature/build_basic_python_api_wrapper

---
