// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Sirac Ozmen
//
// Eight-lane f32 vectors under a bit law: every operation is a
// single-rounding IEEE op with IDENTICAL semantics on every backend.
// The solver kernels are written once against this API; AVX2, NEON
// and the scalar fallback must be indistinguishable in their bits,
// and CI holds that as a hard gate (the sanitize cell runs the scalar
// backend and its hashes join the cross-platform comparison).
//
// Rules that keep the law:
// - min/max are compare+select, NEVER the native instructions: SSE
//   and NEON disagree about NaN propagation and signed zero, and
//   MSVC on arm64 lowers the ternary differently.
// - fused multiply-add is EXPLICIT and used identically everywhere:
//   _mm256_fmadd_ps, vfmaq_f32 and fmaf are all correctly rounded, so
//   they agree bit for bit. Implicit contraction stays forbidden by
//   the compiler flags; only this header spells fma.
// - negation is a sign flip (exact), so composed forms like
//   a*b - c == fma(a, b, -c) hold exactly on all three backends.

#ifndef @OPT@_SRC_SIMD_H
#define @OPT@_SRC_SIMD_H

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#if defined(@OPT@_SIMD_FORCE_SCALAR)
#define @PP@_SIMD_SCALAR 1
#elif defined(__AVX2__) && (defined(__FMA__) || defined(_MSC_VER))
// MSVC defines __AVX2__ under /arch:AVX2 but never __FMA__; the AVX2
// baseline (Haswell+) always ships FMA3.
#define @PP@_SIMD_AVX2 1
#elif defined(__aarch64__) || defined(_M_ARM64)
#define @PP@_SIMD_NEON 1
#else
#define @PP@_SIMD_SCALAR 1
#endif

#if defined(@PP@_SIMD_AVX2)

#include <immintrin.h>

typedef __m256 @P@f8;

static inline @P@f8 @P@F8Load(const float* p)
{
    return _mm256_loadu_ps(p);
}
static inline void @P@F8Store(float* p, @P@f8 v)
{
    _mm256_storeu_ps(p, v);
}
static inline @P@f8 @P@F8Set1(float x)
{
    return _mm256_set1_ps(x);
}
static inline @P@f8 @P@F8Zero(void)
{
    return _mm256_setzero_ps();
}
static inline @P@f8 @P@F8Add(@P@f8 a, @P@f8 b)
{
    return _mm256_add_ps(a, b);
}
static inline @P@f8 @P@F8Sub(@P@f8 a, @P@f8 b)
{
    return _mm256_sub_ps(a, b);
}
static inline @P@f8 @P@F8Mul(@P@f8 a, @P@f8 b)
{
    return _mm256_mul_ps(a, b);
}
static inline @P@f8 @P@F8Neg(@P@f8 a)
{
    return _mm256_xor_ps(a, _mm256_set1_ps(-0.0f));
}
// a * b + c, one rounding.
static inline @P@f8 @P@F8MulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    return _mm256_fmadd_ps(a, b, c);
}
// c - a * b, one rounding.
static inline @P@f8 @P@F8NegMulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    return _mm256_fnmadd_ps(a, b, c);
}
// mask lanes are all-ones or all-zeros; mask ? a : b.
static inline @P@f8 @P@F8Select(@P@f8 mask, @P@f8 a, @P@f8 b)
{
    return _mm256_blendv_ps(b, a, mask);
}
static inline @P@f8 @P@F8GT(@P@f8 a, @P@f8 b)
{
    return _mm256_cmp_ps(a, b, _CMP_GT_OQ);
}
static inline @P@f8 @P@F8LT(@P@f8 a, @P@f8 b)
{
    return _mm256_cmp_ps(a, b, _CMP_LT_OQ);
}
static inline @P@f8 @P@F8EQ(@P@f8 a, @P@f8 b)
{
    return _mm256_cmp_ps(a, b, _CMP_EQ_OQ);
}
static inline @P@f8 @P@F8Div(@P@f8 a, @P@f8 b)
{
    return _mm256_div_ps(a, b);
}
static inline @P@f8 @P@F8Sqrt(@P@f8 a)
{
    return _mm256_sqrt_ps(a);
}
static inline @P@f8 @P@F8And(@P@f8 a, @P@f8 b)
{
    return _mm256_and_ps(a, b);
}

#elif defined(@PP@_SIMD_NEON)

#include <arm_neon.h>

typedef struct @P@f8
{
    float32x4_t lo;
    float32x4_t hi;
} @P@f8;

static inline @P@f8 @P@F8Load(const float* p)
{
    @P@f8 r = {vld1q_f32(p), vld1q_f32(p + 4)};
    return r;
}
static inline void @P@F8Store(float* p, @P@f8 v)
{
    vst1q_f32(p, v.lo);
    vst1q_f32(p + 4, v.hi);
}
static inline @P@f8 @P@F8Set1(float x)
{
    @P@f8 r = {vdupq_n_f32(x), vdupq_n_f32(x)};
    return r;
}
static inline @P@f8 @P@F8Zero(void)
{
    return @P@F8Set1(0.0f);
}
static inline @P@f8 @P@F8Add(@P@f8 a, @P@f8 b)
{
    @P@f8 r = {vaddq_f32(a.lo, b.lo), vaddq_f32(a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8Sub(@P@f8 a, @P@f8 b)
{
    @P@f8 r = {vsubq_f32(a.lo, b.lo), vsubq_f32(a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8Mul(@P@f8 a, @P@f8 b)
{
    @P@f8 r = {vmulq_f32(a.lo, b.lo), vmulq_f32(a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8Neg(@P@f8 a)
{
    @P@f8 r = {vnegq_f32(a.lo), vnegq_f32(a.hi)};
    return r;
}
static inline @P@f8 @P@F8MulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    // vfmaq(c, a, b) = c + a * b, one rounding.
    @P@f8 r = {vfmaq_f32(c.lo, a.lo, b.lo), vfmaq_f32(c.hi, a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8NegMulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    // vfmsq(c, a, b) = c - a * b, one rounding.
    @P@f8 r = {vfmsq_f32(c.lo, a.lo, b.lo), vfmsq_f32(c.hi, a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8Select(@P@f8 mask, @P@f8 a, @P@f8 b)
{
    @P@f8 r;
    r.lo = vbslq_f32(vreinterpretq_u32_f32(mask.lo), a.lo, b.lo);
    r.hi = vbslq_f32(vreinterpretq_u32_f32(mask.hi), a.hi, b.hi);
    return r;
}
static inline @P@f8 @P@F8GT(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    r.lo = vreinterpretq_f32_u32(vcgtq_f32(a.lo, b.lo));
    r.hi = vreinterpretq_f32_u32(vcgtq_f32(a.hi, b.hi));
    return r;
}
static inline @P@f8 @P@F8LT(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    r.lo = vreinterpretq_f32_u32(vcltq_f32(a.lo, b.lo));
    r.hi = vreinterpretq_f32_u32(vcltq_f32(a.hi, b.hi));
    return r;
}
static inline @P@f8 @P@F8EQ(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    r.lo = vreinterpretq_f32_u32(vceqq_f32(a.lo, b.lo));
    r.hi = vreinterpretq_f32_u32(vceqq_f32(a.hi, b.hi));
    return r;
}
static inline @P@f8 @P@F8Div(@P@f8 a, @P@f8 b)
{
    @P@f8 r = {vdivq_f32(a.lo, b.lo), vdivq_f32(a.hi, b.hi)};
    return r;
}
static inline @P@f8 @P@F8Sqrt(@P@f8 a)
{
    @P@f8 r = {vsqrtq_f32(a.lo), vsqrtq_f32(a.hi)};
    return r;
}
static inline @P@f8 @P@F8And(@P@f8 a, @P@f8 b)
{
    @P@f8 r = {
        vreinterpretq_f32_u32(vandq_u32(vreinterpretq_u32_f32(a.lo), vreinterpretq_u32_f32(b.lo))),
        vreinterpretq_f32_u32(vandq_u32(vreinterpretq_u32_f32(a.hi), vreinterpretq_u32_f32(b.hi)))};
    return r;
}

#else // @PP@_SIMD_SCALAR

typedef struct @P@f8
{
    float v[8];
} @P@f8;

static inline @P@f8 @P@F8Load(const float* p)
{
    @P@f8 r;
    memcpy(r.v, p, sizeof(r.v));
    return r;
}
static inline void @P@F8Store(float* p, @P@f8 v)
{
    memcpy(p, v.v, sizeof(v.v));
}
static inline @P@f8 @P@F8Set1(float x)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = x;
    }
    return r;
}
static inline @P@f8 @P@F8Zero(void)
{
    return @P@F8Set1(0.0f);
}
static inline @P@f8 @P@F8Add(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = a.v[i] + b.v[i];
    }
    return r;
}
static inline @P@f8 @P@F8Sub(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = a.v[i] - b.v[i];
    }
    return r;
}
static inline @P@f8 @P@F8Mul(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = a.v[i] * b.v[i];
    }
    return r;
}
static inline @P@f8 @P@F8Neg(@P@f8 a)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = -a.v[i];
    }
    return r;
}
static inline @P@f8 @P@F8MulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = fmaf(a.v[i], b.v[i], c.v[i]);
    }
    return r;
}
static inline @P@f8 @P@F8NegMulAdd(@P@f8 a, @P@f8 b, @P@f8 c)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = fmaf(-a.v[i], b.v[i], c.v[i]);
    }
    return r;
}
static inline @P@f8 @P@F8Select(@P@f8 mask, @P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        uint32_t m;
        uint32_t ua;
        uint32_t ub;
        memcpy(&m, &mask.v[i], 4);
        memcpy(&ua, &a.v[i], 4);
        memcpy(&ub, &b.v[i], 4);
        uint32_t out = (ua & m) | (ub & ~m);
        memcpy(&r.v[i], &out, 4);
    }
    return r;
}
// kind: 1 greater, 0 less, 2 equal.
static inline @P@f8 @P@F8Cmp(int kind, @P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        bool hit = kind == 1 ? a.v[i] > b.v[i] : (kind == 0 ? a.v[i] < b.v[i] : a.v[i] == b.v[i]);
        uint32_t m = hit ? 0xFFFFFFFFu : 0u;
        memcpy(&r.v[i], &m, 4);
    }
    return r;
}
static inline @P@f8 @P@F8GT(@P@f8 a, @P@f8 b)
{
    return @P@F8Cmp(1, a, b);
}
static inline @P@f8 @P@F8LT(@P@f8 a, @P@f8 b)
{
    return @P@F8Cmp(0, a, b);
}
static inline @P@f8 @P@F8EQ(@P@f8 a, @P@f8 b)
{
    return @P@F8Cmp(2, a, b);
}
static inline @P@f8 @P@F8Div(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = a.v[i] / b.v[i];
    }
    return r;
}
static inline @P@f8 @P@F8Sqrt(@P@f8 a)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        r.v[i] = sqrtf(a.v[i]);
    }
    return r;
}
static inline @P@f8 @P@F8And(@P@f8 a, @P@f8 b)
{
    @P@f8 r;
    for (int32_t i = 0; i < 8; ++i)
    {
        uint32_t ua;
        uint32_t ub;
        memcpy(&ua, &a.v[i], 4);
        memcpy(&ub, &b.v[i], 4);
        uint32_t out = ua & ub;
        memcpy(&r.v[i], &out, 4);
    }
    return r;
}

#endif

// Ternary-law min/max: a>b?a:b and a<b?a:b, identical on every
// backend. AVX2's MAXPS and MINPS are defined as exactly that law
// (the second operand when either is NaN or both are zero), so they
// stand in for compare + select. NEON's vmaxq/vminq propagate NaN and
// order signed zeros, so NEON and scalar keep compare + select.
#if defined(@PP@_SIMD_AVX2)
static inline @P@f8 @P@F8Max(@P@f8 a, @P@f8 b)
{
    return _mm256_max_ps(a, b);
}
static inline @P@f8 @P@F8Min(@P@f8 a, @P@f8 b)
{
    return _mm256_min_ps(a, b);
}
#else
static inline @P@f8 @P@F8Max(@P@f8 a, @P@f8 b)
{
    return @P@F8Select(@P@F8GT(a, b), a, b);
}
static inline @P@f8 @P@F8Min(@P@f8 a, @P@f8 b)
{
    return @P@F8Select(@P@F8LT(a, b), a, b);
}
#endif

#endif // @OPT@_SRC_SIMD_H
