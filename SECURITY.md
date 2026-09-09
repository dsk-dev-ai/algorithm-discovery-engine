# Security

The Algorithm Discovery Engine is a pure-`srcs` computation library; it accepts
no network input and stores no data. Security considerations are minimal but
still taken seriously.

## Reporting a vulnerability

If you find a security issue, please do **not** open a public issue. Email or
open a private advisory instead:

- Open a [private security advisory](https://github.com/dsk-dev-ai/algorithm-discovery-engine/security/advisories) on GitHub, or
- Contact the maintainers via a private channel.

We aim to acknowledge reports within 3 business days and release a fix as soon
as a reproduction is available.

## Scope

- Input handling: all inputs are integers/float sequences in-memory.
- No remote calls, no filesystem access at runtime, no secrets.

Thank you for helping keep this project safe.