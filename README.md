# Sovereign Knowledge Compiler Explorer

> An interactive explanation engine that recursively explains how the Sovereign
> Knowledge Compiler works — by compiling itself.

This repository is in the **design / documentation phase**. No application code
has been written. The `/docs` directory contains the complete design
specification required before implementation begins.

## What this is

The Sovereign Knowledge Compiler (SKC) is a compile-time system that organizes
knowledge the way a traditional compiler organizes code: it parses a corpus,
builds intermediate representations, runs deterministic and model-assisted
passes, and emits structured artifacts.

This project's mission is to produce the **first self-explaining SKC
demonstration**. The compiler's first compiled artifact is an interactive
application that *teaches users how the compiler works*, descending from the
highest-level architecture down to the underlying mathematics and computer
science foundations — infinitely explorable, like a curriculum rather than
documentation.

## Repository status

- ✅ Git initialized
- ✅ `/docs` design specification (in progress)
- ⬜ Implementation phase (not started — awaiting review)
- ⬜ No commits created yet
- ⬜ No remote repository created yet

## Documentation

All design documents live in [`/docs`](./docs). Start with:

- [`docs/README.md`](./docs/README.md) — documentation index
- [`docs/PROJECT_VISION.md`](./docs/PROJECT_VISION.md) — mission and thesis
- [`docs/SYSTEM_ARCHITECTURE.md`](./docs/SYSTEM_ARCHITECTURE.md) — layered architecture
- [`docs/COMPILER_PIPELINE.md`](./docs/COMPILER_PIPELINE.md) — the compile pipeline

## Related work (canonical research record)

- Blog: https://www.danielkliewer.com
- Compiler repo: https://github.com/kliewerdaniel/sovereign-knowledge-compiler

## License

To be determined during implementation phase.
