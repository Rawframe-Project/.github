# The Linux toolchain every C and C++ repository of the organization builds
# and tests with in CI. Pinned by date: a repository moves to a new image by
# taking the reusable workflow's new pin, so a toolchain change never lands
# in every repository at once. VERSION changes whenever this file does.
FROM ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac

ARG DEBIAN_FRONTEND=noninteractive

# Compilers, the build tools, and the libraries the families' optional
# components and tests link: X11, Wayland and XCB for windows, ALSA, Pulse
# and PipeWire for audio, lavapipe and the validation layers for Vulkan,
# HarfBuzz and ICU as test oracles.
RUN apt-get update -q \
    && apt-get install -y -q --no-install-recommends \
        ca-certificates curl git git-lfs xz-utils unzip file \
        cmake ninja-build pkg-config ccache make python3 python3-pip python3-venv \
        clang-20 clang-tidy-20 lld-20 libclang-rt-20-dev libclang-rt-20-dev-wasm32 wasi-libc \
        gcc-14 g++-14 gcc-14-multilib g++-14-multilib \
        libx11-dev libx11-data libxrandr-dev libxinerama-dev libxi-dev libxcursor-dev \
        libxkbcommon-dev libxkbcommon-x11-dev xkb-data \
        libxcb1-dev libxcb-cursor-dev libxcb-randr0-dev libxcb-render0-dev libxcb-xfixes0-dev \
        libxcb-xinput-dev libxcb-xkb-dev libxcb-xtest0-dev \
        libwayland-dev wayland-protocols weston xvfb \
        libgl1-mesa-dev mesa-vulkan-drivers vulkan-validationlayers \
        libasound2-dev libpulse-dev libpipewire-0.3-dev \
        libharfbuzz-dev libicu-dev python3-aioquic \
    && rm -rf /var/lib/apt/lists/*

# Unversioned names for the default compilers, and the formatter at the
# version every repository's format check expects.
RUN for t in clang clang++ clang-tidy ld.lld llvm-symbolizer llvm-profdata llvm-cov; do \
        ln -sf "/usr/bin/$t-20" "/usr/local/bin/$t"; \
    done \
    && pip install --no-cache-dir --break-system-packages clang-format==22.1.5 markdown==3.6

ENV CC=clang CXX=clang++ CCACHE_DIR=/ccache CCACHE_MAXSIZE=2G CCACHE_COMPILERCHECK=content
