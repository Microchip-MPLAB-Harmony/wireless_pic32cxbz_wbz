    // Initialize RF System
    SYS_Load_Cal(${WSS_ENABLE_MODE});
 
 <#if PIC32CX_BZ2_HPA_DEVICE == true>
    //Enable the FEM module control for HPA module.
    RF_HpaInit();

</#if>
    // Set up OSAL for RF Stack Library usage
    osalAPIList.OSAL_CRIT_Enter      = OSAL_CRIT_Enter;
    osalAPIList.OSAL_CRIT_Leave      = OSAL_CRIT_Leave;

    osalAPIList.OSAL_SEM_Create      = OSAL_SEM_Create;
    osalAPIList.OSAL_SEM_Pend        = OSAL_SEM_Pend;
    osalAPIList.OSAL_SEM_Post        = OSAL_SEM_Post;
    osalAPIList.OSAL_SEM_PostISR     = OSAL_SEM_PostISR;
    osalAPIList.OSAL_SEM_GetCount    = OSAL_SEM_GetCount;

    osalAPIList.OSAL_QUEUE_Create    = OSAL_QUEUE_Create;
    osalAPIList.OSAL_QUEUE_Send      = OSAL_QUEUE_Send;
    osalAPIList.OSAL_QUEUE_SendISR   = OSAL_QUEUE_SendISR;
    osalAPIList.OSAL_QUEUE_Receive   = OSAL_QUEUE_Receive;
    osalAPIList.OSAL_QUEUE_IsFullISR = OSAL_QUEUE_IsFullISR;
    osalAPIList.OSAL_QUEUE_CreateSet = OSAL_QUEUE_CreateSet;
    osalAPIList.OSAL_QUEUE_AddToSet  = OSAL_QUEUE_AddToSet;
    osalAPIList.OSAL_QUEUE_SelectFromSet = OSAL_QUEUE_SelectFromSet;

    osalAPIList.OSAL_MemAlloc = OSAL_Malloc;
    osalAPIList.OSAL_MemFree = OSAL_Free;
<#if SYSTEM_ENABLE_PMUMODE_SETTING == true>

    // Set Power mode of the system
    PMU_Set_Mode(${SYSTEM_PMU_MODE});
</#if>
<#if (ENABLE_DEEP_SLEEP == true)>
	<#if PIC32CX_BZ3_DEVICE == true>

	//Config retention RAM size
	PMU_REGS->PMU_WCMSIZ &= ~PMU_WCMSIZ_SRAM1_SIZ_Msk;
	<#if (TOTAL_RETENTION_RAM == true)>
	PMU_REGS->PMU_WCMSIZ |= PMU_WCMSIZ_SRAM1_SIZ_32K_SRAM;
	<#else>
	PMU_REGS->PMU_WCMSIZ |= PMU_WCMSIZ_SRAM1_SIZ_16K_SRAM;
	</#if>
	</#if>
</#if>

