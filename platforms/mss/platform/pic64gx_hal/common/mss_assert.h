/*******************************************************************************
 * Copyright 2019-2024 Microchip Technology Inc.
 *
 * SPDX-License-Identifier: MIT
 *
 * PIC64GX HAL Embedded Software
 *
 */

#ifndef HAL_ASSERT_HEADER
#define HAL_ASSERT_HEADER

#ifdef __cplusplus
extern "C" {
#endif

/***************************************************************************//**
 * ASSERT() implementation.
 ******************************************************************************/
/* Disable assertions if we do not recognize the compiler. */
#if defined ( __GNUC__ )
#if defined(NDEBUG)
#define ASSERT(CHECK)
#else
#define ASSERT(CHECK)\
    do { \
        if (!(CHECK)) \
        { \
            __asm volatile ("ebreak"); \
        }\
    } while(0);
#endif /* NDEBUG check */
#endif /* compiler check */

#ifdef __cplusplus
}
#endif

#endif  /* HAL_ASSERT_HEADER */

