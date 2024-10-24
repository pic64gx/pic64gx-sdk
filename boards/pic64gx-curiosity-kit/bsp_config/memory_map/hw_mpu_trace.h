/*******************************************************************************
 * Copyright 2019-2024 Microchip Technology Inc.
 *
 * SPDX-License-Identifier: MIT
 *
 * PIC64GX HSS Embedded Software
 *
 */

#ifndef HW_MPU_TRACE_H_
#define HW_MPU_TRACE_H_

#if !defined (BSP_SETTING_TRACE_MPU_CFG_PMP0)
/*mpu setup register, 64 bits */
#define BSP_SETTING_TRACE_MPU_CFG_PMP0    0x1F00000FFFFFFFFFULL
    /* PMP                               [0:38]  RW value= 0xFFFFFFFFF */
    /* RESERVED                          [38:18] RW value= 0x0 */
    /* MODE                              [56:8]  RW value= 0x1F */
#endif
#if !defined (BSP_SETTING_TRACE_MPU_CFG_PMP1)
/*mpu setup register, 64 bits */
#define BSP_SETTING_TRACE_MPU_CFG_PMP1    0x1F00000FFFFFFFFFULL
    /* PMP                               [0:38]  RW value= 0xFFFFFFFFF */
    /* RESERVED                          [38:18] RW value= 0x0 */
    /* MODE                              [56:8]  RW value= 0x1F */
#endif

#endif /* #ifdef HW_MPU_TRACE_H_ */
