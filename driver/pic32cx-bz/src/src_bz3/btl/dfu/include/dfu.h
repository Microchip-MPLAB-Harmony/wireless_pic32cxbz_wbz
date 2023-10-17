
#include "mem_interface.h"

#ifndef _DFU_H
#define _DFU_H

void dfu(const IMG_MEM_TOPOLOGY ** tops, uint8_t count);
extern int32_t program_exec_main(const IMG_MEM_TOPOLOGY ** tops, uint8_t count);


#endif
