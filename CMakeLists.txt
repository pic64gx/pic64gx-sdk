cmake_minimum_required(VERSION 3.27.1)

list(APPEND _MSS_DRIVERS)

if(${CONFIG_MSS_CAN})
    file(GLOB_RECURSE MSS_CAN_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_can/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_CAN_DRIVERS})
endif()

if(${CONFIG_MSS_ETHERNET_MAC})
    file(GLOB_RECURSE MSS_ETHERNET_MAC_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_ethernet_mac/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_ETHERNET_MAC_DRIVERS})
endif()

if(${CONFIG_MSS_GPIO})
    file(GLOB_RECURSE MSS_GPIO_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_gpio/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_GPIO_DRIVERS})
endif()
    
if(${CONFIG_MSS_I2C})
    file(GLOB_RECURSE MSS_I2C_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_i2c/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_I2C_DRIVERS})
endif()
    
if(${CONFIG_MSS_MMC})
    file(GLOB_RECURSE MSS_MMC_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_mmc/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_MMC_DRIVERS})
endif()
    
if(${CONFIG_MSS_MMUART})
    file(GLOB_RECURSE MSS_MMUART_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_mmuart/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_MMUART_DRIVERS})
endif()

if(${CONFIG_MSS_PDMA})
    file(GLOB_RECURSE MSS_PDMA_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_pdma/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_PDMA_DRIVERS})
endif()
    
if(${CONFIG_MSS_QSPI})
    file(GLOB_RECURSE MSS_QSPI_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_qspi/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_QSPI_DRIVERS})
endif()
    
if(${CONFIG_MSS_RTC})
    file(GLOB_RECURSE MSS_RTC_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_rtc/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_RTC_DRIVERS})
endif()

if(${CONFIG_MSS_SPI})
    file(GLOB_RECURSE MSS_SPI_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_spi/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_SPI_DRIVERS})
endif()

if(${CONFIG_MSS_SYS_SERVICES})
    file(GLOB_RECURSE MSS_SYS_SERVICES_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_sys_services/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_SYS_SERVICES_DRIVERS})
endif()

if(${CONFIG_MSS_TIMER})
    file(GLOB_RECURSE MSS_TIMER_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_timer/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_TIMER_DRIVERS})
endif()

if(${CONFIG_MSS_USB})
    file(GLOB_RECURSE MSS_USB_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_usb/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_USB_DRIVERS})
endif()

if(${CONFIG_MSS_WATCHDOG})
    file(GLOB_RECURSE MSS_WATCHDOG_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/mss_watchdog/*.c)
    list(APPEND _MSS_DRIVERS ${MSS_WATCHDOG_DRIVERS})
endif()

if(${CONFIG_PF_PCIE})
    file(GLOB_RECURSE PF_PCIE_DRIVERS ${WORKSPACE}/platforms/mss/platform/drivers/mss/pf_pcie/*.c)
    list(APPEND _MSS_DRIVERS ${PF_PCIE_DRIVERS})
endif()

file(GLOB_RECURSE _HAL ${WORKSPACE}/platforms/mss/platform/hal/*.c)
file(GLOB_RECURSE _MPFS_HAL ${WORKSPACE}/platforms/mss/platform/mpfs_hal/*.c)
file(GLOB_RECURSE _ASSEM ${WORKSPACE}/platforms/mss/platform/*.S)

set(MSS_DRIVERS ${_MSS_DRIVERS} PARENT_SCOPE)
set(HAL ${_HAL} PARENT_SCOPE)
set(MPFS_HAL ${_MPFS_HAL} PARENT_SCOPE)
set(ASSEM ${_ASSEM} PARENT_SCOPE)
