


/*******************************************************************************
  Function:
    void PCHE_Setup ( void )

  Summary:
    Configure the PCHE_CHECON register based on the configured system clock.

  Remarks:
    This ramfunc function requires XC32 compiler v3.00 or greater.

    The ramfunc attribute is required to allow sufficient time after clearing
    the ADRWS bit before any other bus activity occurs. Refer to Prefetch
    cache module section in PIC32CX-BZ2 Family Errata.
*/

__attribute__((ramfunc, long_call, section(".ramfunc"),unique_section)) void PCHE_Setup(void)
{

    // Set Flash Wait states and enable pre-fetch
    // clear PFMWS and ADRWS
    PCHE_REGS->PCHE_CHECON = (PCHE_REGS->PCHE_CHECON & (~(PCHE_CHECON_PFMWS_Msk | PCHE_CHECON_ADRWS_Msk | PCHE_CHECON_PREFEN_Msk))) 
                                    | (PCHE_CHECON_PFMWS(1) | PCHE_CHECON_PREFEN(1));
    // write completion delay
    for(int i=1; i<10; i++)
    {
        asm ("NOP");
    }

}

<#if ENABLE_DEEP_SLEEP == true>
void _on_reset(void)
{
    //Need to clear register before configure any GPIO
    DEVICE_ClearDeepSleepReg();

    // Initialize the RF Clock Generator
    SYS_ClkGen_Config();

    /* Can't call a RAM function before __pic32c_data_initialization
       Must call a flash function, but in A0 HW version, RAM function is required to avoid HW issue.
       Thus, will not config PCHE before __pic32c_data_initialization in A0 version.
    */
    // Configure Prefetch, Wait States
    if (DSU_REGS->DSU_DID & DSU_DID_REVISION_Msk)   //A1 and later version
    {
        PCHE_REGS->PCHE_CHECON = (PCHE_REGS->PCHE_CHECON & (~(PCHE_CHECON_PFMWS_Msk | PCHE_CHECON_ADRWS_Msk | PCHE_CHECON_PREFEN_Msk))) 
                                        | (PCHE_CHECON_PFMWS(1) | PCHE_CHECON_PREFEN(1));
    }
}
</#if>