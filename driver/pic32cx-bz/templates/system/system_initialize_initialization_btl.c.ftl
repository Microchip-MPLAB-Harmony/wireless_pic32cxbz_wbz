


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

typedef void (*p_function)(void);

/*******************************************************************************
  Function:
    void _on_reset ( void )

  Summary:
    Function which gets called from Reset_Handler in startup_xc32.c.

  Remarks:
    None.
*/
void _on_reset(void)
{
    if ((RCON_REGS->RCON_RCON & RCON_RCON_DPSLP_Msk) == RCON_RCON_DPSLP_Msk)
    {
        uint32_t jump_address = *(__IO uint32_t*)(SLOT0_FIRMWARE + 4);
        /* Assign Slot0 firmware address to function pointer */
        p_function p_jump_function = (p_function)jump_address;

        /* Jump to the application */
        p_jump_function();
    }

}