# CHANGELOG


## v0.0.0 (2026-01-03)

### Unknown

* Fix YAML syntax error in release workflow from unindented heredoc content (#7)

* Initial plan

* Fix YAML syntax errors in release.yml workflow file

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: famda <26621392+famda@users.noreply.github.com> ([`82aa396`](https://github.com/famda/platform-cli/commit/82aa39694432884f2f15841ebadbc7386087929c))

* Add CI/CD pipeline with semantic versioning and per-OS release artifacts (#5)

* Initial plan

* feat: add CI/CD workflows with semantic versioning and per-OS releases

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: remove unnecessary deactivate commands in release workflow

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: use direct venv pip paths in release workflow for GitHub Actions compatibility

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: remove template_dir reference and use uv pip for consistency

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: use uv build in semantic-release build_command for consistency

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: use Set-Content for PowerShell strings to avoid parsing issues

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: enable variable substitution in heredoc and use UTF8 encoding consistently

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: add explicit GITHUB_TOKEN permissions to workflows for security

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: use bash shell for verify package step to ensure glob pattern works on Windows

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* fix: apply code review suggestions - use -m semantics, pin uv version, remove unused artifact_name, fix trailing space

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: famda <26621392+famda@users.noreply.github.com> ([`1d9d22c`](https://github.com/famda/platform-cli/commit/1d9d22c817845459b63d4896f760bd90d789e494))

* Create Python CLI base structure with uv and modular architecture (#2)

* Initial plan

* Create base Python CLI structure with uv, tests, and modules

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Add uv.lock file for reproducible builds

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Update README to reflect multi-format file support (#3)

* Initial plan

* Update README to reflect support for multiple file types

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Fix comment consistency in usage examples

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Apply code review feedback: fix build backend, remove unused imports, update entry point

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Add mandatory input/output validation and update module signatures

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Add integration tests for main() function orchestration logic

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

* Fix unreachable code and improve test implementation

Co-authored-by: famda <26621392+famda@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: famda <26621392+famda@users.noreply.github.com> ([`9cd6cb9`](https://github.com/famda/platform-cli/commit/9cd6cb9db7e9b364c1625560f9fec5c6816a1db0))

* Initial commit ([`83b0a17`](https://github.com/famda/platform-cli/commit/83b0a17fd5f34f40c3e7a7c9d57a2a000e9b533c))
