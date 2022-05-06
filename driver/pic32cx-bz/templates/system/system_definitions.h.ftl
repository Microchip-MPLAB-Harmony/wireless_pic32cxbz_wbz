#include "driver/device_support/include/info_block.h"
#include "driver/device_support/include/pmu_system.h"
#include "driver/device_support/include/rf_system.h"
#include "driver/device_support/include/sleep_system.h"
#include "framework_defs.h"
#include "app_idle_task.h"
<#if SLEEP_SUPPORTED>
#include "device_sleep.h"
</#if>
<#if ENABLE_DEEP_SLEEP>
#include "device_deep_sleep.h"
</#if>
