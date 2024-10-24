#include "pic64gx_hal/mss_hal.h"
#include "mss_mmuart/mss_uart.h"


const uint8_t g_message[] = "\r\n Hello, World!\r\n";

void e51(void)
{
    (void) mss_config_clk_rst(MSS_PERIPH_MMUART0, (uint8_t) 1, PERIPHERAL_ON);

    MSS_UART_init(&g_mss_uart0_lo,
    MSS_UART_115200_BAUD,
    MSS_UART_DATA_8_BITS | MSS_UART_NO_PARITY | MSS_UART_ONE_STOP_BIT);

    /* Message on uart0 */
    MSS_UART_polled_tx(&g_mss_uart0_lo, g_message, sizeof(g_message));

    while (1U)
    {

    }
}
