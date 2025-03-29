#include <stdint.h>
#include <stdbool.h>
#include "dfu/dfu.h"
#include "configuration.h"
#include "definitions.h"
#include "application.h"

void dfu(const IMG_MEM_TOPOLOGY ** tops, uint8_t count)
{
    if (count && tops)   
        program_exec_main(tops, count);
    
    critical_error(BOOT_ERROR_CRITICAL_FAILURE);
    critical_error(BOOT_ERROR_CRITICAL_FAILURE);
}
    
    