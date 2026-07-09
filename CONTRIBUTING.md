# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`).
4. Test you contribution.
5. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [black](https://github.com/ambv/black) to make sure the code follows the style.

## Test your code modification

This custom component is based on [chime_tts template](https://github.com/ludeeus/chime_tts).

It comes with development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

## Compatibility strategy

Compatibility issues are one of the hardest things to reproduce locally, so the
project now tests the integration in two complementary ways:

1. `tox` compatibility matrix
   This runs the unit/integration test suite against a representative Home
   Assistant floor/current/latest stack so API drift shows up before release.

2. Docker-backed Home Assistant smoke tests
   These boot real `stable` and `dev` Home Assistant containers and run the live
   end-to-end suite against the actual integration.

Useful local commands:

- `make matrix`
- `make test-e2e`
- `./scripts/ha-docker stable pull`
- `./scripts/ha-docker dev pull`

If you are investigating a user report, try to add a focused regression test to
the regular pytest suite first, then add or extend a Docker E2E case when the
issue depends on real Home Assistant runtime behavior.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
