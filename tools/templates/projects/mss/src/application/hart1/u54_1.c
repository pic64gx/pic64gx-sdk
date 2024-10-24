#include "pic64gx_hal/mss_hal.h"

void u54_1(void)
{
    clear_soft_interrupt();

    set_csr(mie, MIP_MSIP);

    while (1u)
    {

    }
}
