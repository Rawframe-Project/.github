// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Sirac Ozmen
//
// DEFLATE (RFC 1951) in a zlib stream (RFC 1950), as PNG images and FBX
// arrays hold it (a family file): stored, fixed and dynamic Huffman
// blocks inflated into a buffer whose size the caller knows, every
// length, distance and code checked against the input and the output,
// and the stream's Adler-32 checked against what it gave. It allocates
// nothing.

#ifndef @OPT@_SRC_INFLATE_H
#define @OPT@_SRC_INFLATE_H

#include "@LIB@/base.h"

#include <stddef.h>
#include <stdint.h>

// Inflates a zlib stream into exactly outSize bytes: @P@_success when
// the stream ends, filling them, and its checksum matches; otherwise
// @P@_errorFormat, out's bytes unspecified.
@P@Result @P@InflateZlib(const uint8_t* in, size_t inSize, uint8_t* out, size_t outSize);

#endif // @OPT@_SRC_INFLATE_H
