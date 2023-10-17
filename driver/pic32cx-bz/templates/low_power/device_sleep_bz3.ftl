/*******************************************************************************
  Sleep System Source File

  Company:
    Microchip Technology Inc.

  File Name:
    device_sleep.c

  Summary:
    This file contains the Device Sleep functions.

  Description:
    This file contains the Device Sleep functions.
 *******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2022 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include <string.h>
#include "device.h"
#include "definitions.h"


// *****************************************************************************
// *****************************************************************************
// Section: macro
// *****************************************************************************
// *****************************************************************************
#define CLK_READY_RETRIES  8000
#define BTZB_XTAL_NOT_READY ((BTZBSYS_REGS->BTZBSYS_SUBSYS_STATUS_REG1 \
                            & BTZBSYS_SUBSYS_STATUS_REG1_xtal_ready_out_Msk) \
                            != BTZBSYS_SUBSYS_STATUS_REG1_xtal_ready_out_Msk)
#define BTZB_PLL_NOT_LOCKED ((BTZBSYS_REGS->BTZBSYS_SUBSYS_STATUS_REG1 \
                            & BTZBSYS_SUBSYS_CNTRL_REG1_subsys_dbg_bus_sel_top_Msk) \
                            != BTZBSYS_SUBSYS_CNTRL_REG1_subsys_dbg_bus_sel_top_Msk)

#define BLE_SPI_ADDR_REG    ( * ( ( volatile uint16_t * ) 0x41013002UL ) )
#define BLE_SPI_W_DATA_REG  ( * ( ( volatile uint16_t * ) 0x41013000UL ) )
#define BLE_SPI_R_DATA_REG  ( * ( ( volatile uint16_t * ) 0x41013028UL ) )
#define BLE_RFPWRMGMT_REG   ( * ( ( volatile uint32_t * ) 0x41013004UL ) )


/* The action ID for enter/exit sleep. */
typedef enum DEVICE_SLEEP_ActionId_T
{
    DEVICE_SLEEP_ENTER_SLEEP,                           /**< Enter sleep. */
    DEVICE_SLEEP_EXIT_SLEEP                             /**< Exit sleep. */
} DEVICE_SLEEP_ActionId_T;

/* The definition of clock source  */
typedef enum DEVICE_ClkSrcId_T
{
    DEVICE_NO_CLK = 0x00,                                /**< No clock is selected. */
    DEVICE_CLK_REFO1,                                    /**< REFO1 is selected. */
    DEVICE_CLK_REFO2,                                    /**< REFO2 is selected. */
    DEVICE_CLK_REFO3,                                    /**< REFO3 is selected. */
    DEVICE_CLK_REFO4,                                    /**< REFO4 is selected. */
    DEVICE_CLK_REFO5,                                    /**< REFO5 is selected. */
    DEVICE_CLK_REFO6,                                    /**< REFO6 is selected. */
    DEVICE_CLK_LPCLK,                                    /**< Low power clock is selected. */
    DEVICE_CLK_END
} DEVICE_ClkSrcId_T;

/* Peripheral enable/disable settings of PMD3. */
typedef struct DEVICE_Pmd3Reg_T
{
    uint8_t sercom0: 1;                                  /**< SERCOM 0. */
    uint8_t sercom1: 1;                                  /**< SERCOM 1. */
    uint8_t sercomi2c: 1;                                /**< SERCOM I2C. */
    uint8_t dac: 1;                                      /**< DAC. */
    uint8_t tc0: 1;                                      /**< TC 0. */
    uint8_t tc1: 1;                                      /**< TC 1. */
    uint8_t tc2: 1;                                      /**< TC 2. */
    uint8_t tc3: 1;                                      /**< TC 3. */
    uint8_t tc4: 1;                                      /**< TC 4. */
    uint8_t tc5: 1;                                      /**< TC 5. */
    uint8_t tc6: 1;                                      /**< TC 6. */
    uint8_t tc7: 1;                                      /**< TC 7. */
    uint8_t tcc0: 1;                                     /**< TCC 0. */
    uint8_t tcc1: 1;                                     /**< TCC 1. */
    uint8_t tcc2: 1;                                     /**< TCC 2. */
    uint8_t reserved: 1;                                 /**< Reserved. */
} DEVICE_Pmd3Reg_T;


// *****************************************************************************
// *****************************************************************************
// Section: Global Variables
// *****************************************************************************
// *****************************************************************************
static uint32_t s_pmd1Backup;
static uint32_t s_pmd2Backup;
static uint32_t s_pmd3Backup;

static uint32_t s_refo1Backup;
static uint32_t s_refo2Backup;
static uint32_t s_refo3Backup;
static uint32_t s_refo4Backup;
static uint32_t s_refo5Backup;
static uint32_t s_refo6Backup;

static uint8_t s_adcCpBackup;
static uint16_t s_rfRegBackup[6];

// *****************************************************************************
// *****************************************************************************
// Section: Functions
// *****************************************************************************
// *****************************************************************************
static void device_Delay(uint32_t value)
{
    uint32_t i;

    for (i = 0; i < value; i++)
    {
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();
        __NOP();

    }
} 

/* Unlock system for clock configuration */
static void devie_SysUnlock(void)
{
    CFG_REGS->CFG_SYSKEY = 0x00000000;
    CFG_REGS->CFG_SYSKEY = 0xAA996655;
    CFG_REGS->CFG_SYSKEY = 0x556699AA;
}

static void devie_SysLock(void)
{
    CFG_REGS->CFG_SYSKEY = 0x33333333;
}

/* Configure Reference Oscillator Control Register */
static void device_configRefOscReg(DEVICE_SLEEP_ActionId_T action)
{
    if (action == DEVICE_SLEEP_ENTER_SLEEP)
    {
        s_refo1Backup = 0;
        s_refo2Backup = 0;
        s_refo3Backup = 0;
        s_refo4Backup = 0;
        s_refo5Backup = 0;
        s_refo6Backup = 0;

        //REFO1CON
        if ((CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_ON_Msk) && (!(CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo1Backup = CRU_REGS->CRU_REFO1CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO1CONCLR = CRU_REFO1CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO1CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }

        //REFO2CON
        if ((CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_ON_Msk) && (!(CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo2Backup = CRU_REGS->CRU_REFO2CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO2CONCLR = CRU_REFO2CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO2CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }

        //REFO3CON
        if ((CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_ON_Msk) && (!(CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo3Backup = CRU_REGS->CRU_REFO3CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO3CONCLR = CRU_REFO3CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO3CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }

        //REFO4CON
        if ((CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_ON_Msk) && (!(CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo4Backup = CRU_REGS->CRU_REFO4CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO4CONCLR = CRU_REFO4CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO4CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }

        //REFO5CON
        if ((CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_ON_Msk) && (!(CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo5Backup = CRU_REGS->CRU_REFO5CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO5CONCLR = CRU_REFO5CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO5CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }

        //REFO6CON
        if ((CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_ON_Msk) && (!(CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_RSLP_Msk)))
        {
            //Disable REFOxCON in sleep mode

            //Backup REFOxCON
            s_refo6Backup = CRU_REGS->CRU_REFO6CON;

            //Can't update REFOxCON register if REFOxCON.ACTIVE != REFOxCON.ON
            while (!(CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_ACTIVE_Msk));
            CRU_REGS->CRU_REFO6CONCLR = CRU_REFO6CON_ON_Msk;    //Disable REFOxCON

            while (CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_ACTIVE_Msk);
            CRU_REGS->CRU_REFO6CONCLR = 0xFFFFFEFF;   //Clear REFOxCON (Bit 8 is read only)
        }
    }
    else
    {
        //Check if it needs to restore REFOx
        //REFO1CON
        if ((s_refo1Backup & CRU_REFO1CON_ON_Msk) && (!(s_refo1Backup & CRU_REFO1CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo1Backup &= ~(CRU_REFO1CON_ON_Msk | CRU_REFO1CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO1CON = s_refo1Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO1CONSET = CRU_REFO1CON_ON_Msk;
        }

        //REFO2CON
        if ((s_refo2Backup & CRU_REFO2CON_ON_Msk) && (!(s_refo2Backup & CRU_REFO2CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo2Backup &= ~(CRU_REFO2CON_ON_Msk | CRU_REFO2CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO2CON = s_refo2Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO2CONSET = CRU_REFO2CON_ON_Msk;
        }

        //REFO3CON
        if ((s_refo3Backup & CRU_REFO3CON_ON_Msk) && (!(s_refo3Backup & CRU_REFO3CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo3Backup &= ~(CRU_REFO3CON_ON_Msk | CRU_REFO3CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO3CON = s_refo3Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO3CONSET = CRU_REFO3CON_ON_Msk;
        }

        //REFO4CON
        if ((s_refo4Backup & CRU_REFO4CON_ON_Msk) && (!(s_refo4Backup & CRU_REFO4CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo4Backup &= ~(CRU_REFO4CON_ON_Msk | CRU_REFO4CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO4CON = s_refo4Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO4CONSET = CRU_REFO4CON_ON_Msk;
        }

        //REFO5CON
        if ((s_refo5Backup & CRU_REFO5CON_ON_Msk) && (!(s_refo5Backup & CRU_REFO5CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo5Backup &= ~(CRU_REFO5CON_ON_Msk | CRU_REFO5CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO5CON = s_refo5Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO5CONSET = CRU_REFO5CON_ON_Msk;
        }

        //REFO6CON
        if ((s_refo6Backup & CRU_REFO6CON_ON_Msk) && (!(s_refo6Backup & CRU_REFO6CON_RSLP_Msk)))
        {
            //Exclude output enable and active(read only) bit 
            s_refo6Backup &= ~(CRU_REFO6CON_ON_Msk | CRU_REFO6CON_ACTIVE_Msk);

            //Restore REFOx setting
            CRU_REGS->CRU_REFO6CON = s_refo6Backup;

            // Enable oscillator (ON bit)
            CRU_REGS->CRU_REFO6CONSET = CRU_REFO6CON_ON_Msk;
        }
    }
}

/* Check the if peripheral can be keep running in sleep mode. Return true means it can be keep running. */
static bool device_chkPeripheral(DEVICE_ClkSrcId_T select)
{
    uint32_t pmd2Val;

    pmd2Val = CFG_REGS->CFG_PMD2;

    if ((select == DEVICE_CLK_REFO1) && (!(pmd2Val & CFG_PMD2_REFO1MD_Msk)))    //REFO1 is not disabled in sleep mode
        return true;

    else if ((select == DEVICE_CLK_REFO2) && (!(pmd2Val & CFG_PMD2_REFO2MD_Msk)))   //REFO2 is not disabled in sleep mode
        return true;

    else if ((select == DEVICE_CLK_REFO3) && (!(pmd2Val & CFG_PMD2_REFO3MD_Msk)))   //REFO3 is not disabled in sleep mode
        return true;

    else if ((select == DEVICE_CLK_REFO4) && (!(pmd2Val & CFG_PMD2_REFO4MD_Msk)))   //REFO4 is not disabled in sleep mode
        return true;

    else if ((select == DEVICE_CLK_REFO5) && (!(pmd2Val & CFG_PMD2_REFO5MD_Msk)))   //REFO5 is not disabled in sleep mode
        return true;

    else if ((select == DEVICE_CLK_REFO6) && (!(pmd2Val & CFG_PMD2_REFO6MD_Msk)))   //REFO6 is not disabled in sleep mode
        return true;

    else if (select == DEVICE_CLK_LPCLK)   //LPCLK is used
        return true;

    else
        return false;
}

/* Configure PMD Register */
static void device_configPmdReg(DEVICE_SLEEP_ActionId_T action)
{
    if (action == DEVICE_SLEEP_ENTER_SLEEP)
    {
        DEVICE_Pmd3Reg_T pmdReg;
        DEVICE_ClkSrcId_T select;
        uint32_t pmd2Val, pmd3Val;

        memset((uint8_t *)&pmdReg, 0, sizeof(DEVICE_Pmd3Reg_T));

        //For PMD1, disable all PMD except RTC
        CFG_REGS->CFG_PMD1 = 0xFFFEFFFF;   // bit 16: RTC

        //For PMD2
        //Check if RSLP bit is set, do not disable this REFOx
        pmd2Val = 0xFFFFFFFF;

        if ((CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_ON_Msk) && (CRU_REGS->CRU_REFO1CON & CRU_REFO1CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO1MD_Msk;

        if ((CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_ON_Msk) && (CRU_REGS->CRU_REFO2CON & CRU_REFO2CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO2MD_Msk;

        if ((CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_ON_Msk) && (CRU_REGS->CRU_REFO3CON & CRU_REFO3CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO3MD_Msk;

        if ((CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_ON_Msk) && (CRU_REGS->CRU_REFO4CON & CRU_REFO4CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO4MD_Msk;

        if ((CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_ON_Msk) && (CRU_REGS->CRU_REFO5CON & CRU_REFO5CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO5MD_Msk;

        if ((CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_ON_Msk) && (CRU_REGS->CRU_REFO6CON & CRU_REFO6CON_RSLP_Msk))
            pmd2Val &= ~CFG_PMD2_REFO6MD_Msk;

        CFG_REGS->CFG_PMD2 = pmd2Val;


        //For PMD3, check if the peripheral is enabled
        //bit 0~2 of PMD3: SERCOM 0~1 and SERCOM I2C
        //bit 3 of PMD3: DAC //TODO
        //bit 4~11 of PMD3: TC0~7
        //bit 12~14 of PMD3 for TCC0~TCC2

        pmd3Val = 0xFFFF;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_SER0MD_Msk))
            pmdReg.sercom0 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_SER1MD_Msk))
            pmdReg.sercom1 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_SER2MD_Msk))
            pmdReg.sercomi2c = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_DACMD_Msk))    //TODO: DAC doens't need clock
            pmdReg.dac= 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC0MD_Msk))
            pmdReg.tc0 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC1MD_Msk))
            pmdReg.tc1 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC2MD_Msk))
            pmdReg.tc2 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC3MD_Msk))
            pmdReg.tc3 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC4MD_Msk))
            pmdReg.tc4 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC5MD_Msk))
            pmdReg.tc5 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC6MD_Msk))
            pmdReg.tc6 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TC7MD_Msk))
            pmdReg.tc7 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TCC0MD_Msk))
            pmdReg.tcc0 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TCC1MD_Msk))
            pmdReg.tcc1 = 1;

        if (!(CFG_REGS->CFG_PMD3 & CFG_PMD3_TCC2MD_Msk))
            pmdReg.tcc2 = 1;


        //Check CFGPCLKGEN1~4 to check if the peripheral clock is enabled and check its clock source
        //Do not turn the peripheral off if RSLP is set (s_refoxBackup = 0) or CLK SRC is set as LP CLK
        if (pmdReg.sercom0 || pmdReg.sercom1)
        {
            //Check CFGCLKGEN1 bit 15, if enabled, check the clock source by bit 12~14
            if (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_SERCOM01CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_SERCOM01CSEL_Msk) >> CFG_CFGPCLKGEN1_SERCOM01CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    if (pmdReg.sercom0)
                        pmd3Val &= ~CFG_PMD3_SER0MD_Msk;

                    if (pmdReg.sercom1)
                        pmd3Val &= ~CFG_PMD3_SER1MD_Msk;
                }
            }
        }

        if (pmdReg.sercomi2c)
        {
            //Check CFGCLKGEN1 bit 19, if enabled, check the clock source by bit 16~18
            if (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_SERCOM2CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_SERCOM2CSEL_Msk) >> CFG_CFGPCLKGEN1_SERCOM2CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    pmd3Val &= ~CFG_PMD3_SER2MD_Msk;
                }
            }
        }

        //TODO: DAC doesn't need clock, thus, we don't know if it should be disabled in standby sleep mode or not.
        if (pmdReg.dac)
        {
            //pmd3Val &= ~CFG_PMD3_DACMD_Msk;    //Keep DAC enabled
        }


        if (pmdReg.tc0)
        {
            //Check CFGCLKGEN4 bit 3, if enabled, check the clock source by bit 0~2
            if (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC0CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC0CSEL_Msk) >> CFG_CFGPCLKGEN4_TC0CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    pmd3Val &= ~CFG_PMD3_TC0MD_Msk;
                }
            }
        }

        if (pmdReg.tc1)
        {
            //Check CFGCLKGEN4 bit 7, if enabled, check the clock source by bit 4~6
            if (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC1CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC1CSEL_Msk) >> CFG_CFGPCLKGEN4_TC1CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    pmd3Val &= ~CFG_PMD3_TC1MD_Msk;
                }
            }
        }

        if (pmdReg.tc2 || pmdReg.tc3)
        {
            //Check CFGCLKGEN4 bit 11, if enabled, check the clock source by bit 8~10
            if (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC23CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC23CSEL_Msk) >> CFG_CFGPCLKGEN4_TC23CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    if (pmdReg.tc2)
                        pmd3Val &= ~CFG_PMD3_TC2MD_Msk;

                    if (pmdReg.tc3)
                        pmd3Val &= ~CFG_PMD3_TC3MD_Msk;
                }
            }
        }

        if (pmdReg.tc4 || pmdReg.tc5)
        {
            //Check CFGCLKGEN4 bit 15, if enabled, check the clock source by bit 12~14
            if (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC54CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC54CSEL_Msk) >> CFG_CFGPCLKGEN4_TC54CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    if (pmdReg.tc4)
                        pmd3Val &= ~CFG_PMD3_TC4MD_Msk;

                    if (pmdReg.tc5)
                        pmd3Val &= ~CFG_PMD3_TC5MD_Msk;
                }
            }
        }

        if (pmdReg.tc6 || pmdReg.tc7)
        {
            //Check CFGCLKGEN4 bit 19, if enabled, check the clock source by bit 18~16
            if (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC67CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN4 & CFG_CFGPCLKGEN4_TC67CSEL_Msk) >> CFG_CFGPCLKGEN4_TC67CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    if (pmdReg.tc6)
                        pmd3Val &= ~CFG_PMD3_TC6MD_Msk;

                    if (pmdReg.tc7)
                        pmd3Val &= ~CFG_PMD3_TC7MD_Msk;
                }
            }
        }

        if (pmdReg.tcc0)
        {
            //Check CFGCLKGEN3 bit 23, if enabled, check the clock source by bit 20~22
            if (CFG_REGS->CFG_CFGPCLKGEN3 & CFG_CFGPCLKGEN3_TCC0CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN3 & CFG_CFGPCLKGEN3_TCC0CSEL_Msk) >> CFG_CFGPCLKGEN3_TCC0CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    pmd3Val &= ~CFG_PMD3_TCC0MD_Msk;
                }
            }
        }

        if (pmdReg.tcc1 || pmdReg.tcc2)
        {
            //Check CFGCLKGEN1 bit 23, if enabled, check the clock source by bit 20~22
            if (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_TCC12CD_Msk)
            {
                select = (CFG_REGS->CFG_CFGPCLKGEN1 & CFG_CFGPCLKGEN1_TCC12CSEL_Msk) >> CFG_CFGPCLKGEN1_TCC12CSEL_Pos;

                if (device_chkPeripheral(select))
                {
                    if (pmdReg.tcc1)
                        pmd3Val &= ~CFG_PMD3_TCC1MD_Msk;

                    if (pmdReg.tcc2)
                        pmd3Val &= ~CFG_PMD3_TCC2MD_Msk;
                }
            }
        }

        CFG_REGS->CFG_PMD3 = pmd3Val;
    }
    else
    {
        CFG_REGS->CFG_PMD1 = s_pmd1Backup;
        CFG_REGS->CFG_PMD2 = s_pmd2Backup;
        CFG_REGS->CFG_PMD3 = s_pmd3Backup;
    }
}

/* Configure ADC-CP Clock */
static void device_configAdcCpClk(DEVICE_SLEEP_ActionId_T action)
{
     if (action == DEVICE_SLEEP_ENTER_SLEEP)
     {
        s_adcCpBackup = (CRU_REGS->CRU_SPLLCON & CRU_SPLLCON_SPLLPOSTDIV2_Msk) >> CRU_SPLLCON_SPLLPOSTDIV2_Pos;

        if (s_adcCpBackup)
        {
            CRU_REGS->CRU_SPLLCON &= ~CRU_SPLLCON_SPLLPOSTDIV2_Msk;
        }
     }
     else
    {
        if (s_adcCpBackup)
        {
            CRU_REGS->CRU_SPLLCON |= CRU_SPLLCON_SPLLPOSTDIV2(s_adcCpBackup);
        }
    }
}

/* Write to RF register */
static void device_writeRfReg(uint8_t addr, uint16_t value)
{
    BLE_SPI_ADDR_REG = addr;
    BLE_SPI_W_DATA_REG = value;
    BLE_RFPWRMGMT_REG |= 0x00100000;

    while(BLE_RFPWRMGMT_REG & 0x00100000);
}

/* Read from RF register */
static uint16_t device_readRfReg(uint8_t addr)
{
    BLE_SPI_ADDR_REG = addr;
    BLE_RFPWRMGMT_REG |= 0x00040000;

    while(BLE_RFPWRMGMT_REG & 0x00040000);

    return BLE_SPI_R_DATA_REG;
}

/* Configure RF Register */
static void device_configCldo(DEVICE_SLEEP_ActionId_T action)
{
    uint16_t tmp;

    if (action == DEVICE_SLEEP_ENTER_SLEEP)
    {
        tmp = device_readRfReg(0x09);
        s_rfRegBackup[0] = tmp;
        tmp &= ~(1 << 2);
        device_writeRfReg(0x09, tmp); // [2] BIAS_PTAT_Iref_en = 0

        tmp = device_readRfReg(0x15);
        s_rfRegBackup[1] = tmp;
        tmp &= ~((1 << 0) | (1 << 7));
        tmp |= (1 << 11);
        device_writeRfReg(0x15, tmp); // [0] BIAS_tsens_en = 0, [7] BIAS_CTAT_en = 0, [11] CLDO_Vbg_Iref_sel_reg = 1

        tmp = device_readRfReg(0x18);
        s_rfRegBackup[2] = tmp;
        tmp &= ~(1 << 14);
        tmp |= (1 << 13);
        device_writeRfReg(0x18, tmp); // [13] BIAS_BG_en_sel = 1, [14] BIAS_BG_en_reg = 0

        tmp = device_readRfReg(0x22);
        s_rfRegBackup[3] = tmp;
        tmp &= ~(1 << 4);
        device_writeRfReg(0x22, tmp); // [4] Disable RFLDO = 0

        tmp = device_readRfReg(0x2f);
        s_rfRegBackup[4] = tmp;
        tmp |= (1 << 7);
        device_writeRfReg(0x2f, tmp); // [7] CLKGEN_PWDPLL = 1

        tmp = device_readRfReg(0x34);
        s_rfRegBackup[5] = tmp;
        tmp |= (1 << 14);
        device_writeRfReg(0x34, tmp); // [14] CLDO_Vbg_Iref_sel = 1
    }
    else        //Restore the settings
    {
        device_writeRfReg(0x09, s_rfRegBackup[0]);

        device_writeRfReg(0x15, s_rfRegBackup[1]);

        device_writeRfReg(0x18, s_rfRegBackup[2]);

        device_writeRfReg(0x22, s_rfRegBackup[3]);

        device_writeRfReg(0x2f, s_rfRegBackup[4]);

        device_writeRfReg(0x34, s_rfRegBackup[5]);
    }
}

void DEVICE_EnterSleepMode(void)
{
    // unlock key sequence
    devie_SysUnlock();

    // Step 1 : For connected sleep case, if SOSC clock is available on the module, set 32K CLK source to SOSC CLK in CRU and set MLPCLK_MOD to 1 to divide 32.768kHz clock to 32kHz clock to save power. Otherwise, set 32K CLK source to POSC CLK in CRU to ensure accuracy of 32K CLK
    //          For unconnected sleep case, set 32K CLK source to LPRC CLK in CRU to save power since accuracy requirement does not need to be met
    // step 1 has moved to CLK_Initialize()
    // Some steps are executed within library

    // Step 6 : Disable bt_zb_dbg bus toggling
    DEVICE_SLEEP_DisableDebugBus();

    // Step 14 : Disable PCHE Cache, which is proposed by SOC team for low power optimization
    PCHE_REGS->PCHE_CHECON = 0xf;
    
    // Step 15 : Set PB1 CLK to SYS_CLK/5, which is proposed by SOC team for low power optimization
    CRU_REGS->CRU_PB1DIV = 0x8804;

    // Step 16 : set REFOx registers to 0, combining step 17 to de-assert external PLL request 
    // since we don't know how and when plib_clock will be changed. so we will backup all 6 sets REFOx registers.
    // Ensure the Reference Clock Out Module is enabled, REFO1 Clock is selected by CFG_CFGPCLKGEN1

    // Check PMD lock bit
    if (CFG_REGS->CFG_CFGCON0 & CFG_CFGCON0_PMDLOCK_Msk)
    {
        // PMD lock is enabled, check CFGCLOCK
        if ((CFG_REGS->CFG_CFGCON0 & CFG_CFGCON0_CFGCLOCK_Msk) == 0)
        {
            // Disable PMD lock
            CFG_REGS->CFG_CFGCON0 &= ~CFG_CFGCON0_PMDLOCK_Msk;
        }
    }

    if (CFG_REGS->CFG_PMD2 & CFG_PMD2_REFO1MD_Msk)
    {
        // Enable PMD2_REFO1
        CFG_REGS->CFG_PMD2 &= ~CFG_PMD2_REFO1MD_Msk;
    }

    // Store all PMD setting
    s_pmd1Backup = CFG_REGS->CFG_PMD1;
    s_pmd2Backup = CFG_REGS->CFG_PMD2;
    s_pmd3Backup = CFG_REGS->CFG_PMD3;

    // Backup and Configure REFOxCON register
    device_configRefOscReg(DEVICE_SLEEP_ENTER_SLEEP);

    // Configure PMD register
    device_configPmdReg(DEVICE_SLEEP_ENTER_SLEEP);

    // Configure ADC-CP Clock
    device_configAdcCpClk(DEVICE_SLEEP_ENTER_SLEEP);

    // Step 17 : Change SYS CLK source in CRU from SPLL1 CLK to POSC CLK 
    CRU_REGS->CRU_OSCCON &= (~0xf01); 
    CRU_REGS->CRU_OSCCON |= 0x200;

    // Request oscillator switch to occur
    CRU_REGS->CRU_OSCCONSET = CRU_OSCCON_OSWEN_Msk;

    // Wait for indication of successful clock change before proceeding
    while(CRU_REGS->CRU_OSCCON & CRU_OSCCON_OSWEN_Msk);

    // Step 18 : Set subsys_clk_src_sel to 0 to change subsys clock source from PLL CLK to XTAL CLK
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG1 &= (~0x30);
    
    // Step 19 :Disable CLKGEN Clock enable in RF
    DEVICE_SLEEP_ConfigRfClk(false);

    //Step 19.1 : If XTAL clock is OFF, set subsys_bypass_pll_lock to 0 via subsys config register
    if ((CFG_REGS->CFG_CFGCON4 & 0x3000) == 0x2000) // SOSC : XTAL_OFF
    {
        DEVICE_SLEEP_ConfigSubSysPllLock(false);
    }

    // Step 20 : Set die_BENXOANA_ovrd_en to 1 to switch LDO_PLL to CLDO
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 |= 0x800;

    // Step 21 : Set EN_RFLDO_ovrd_en to 1
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 |= 0x8000;
    
    // Step 22 : Combining step 21, de-assert external PLL power request to disable CLKGEN LDO enable in RF
    CRU_REGS->CRU_SPLLCON |= 0x08; 
    
    // Step 23 : set KEEP_ACLB_CLOCKS_ON to 1 to enable ACLB clocks for SPI access
    DEVICE_SLEEP_ConfigAclbClk(true);

    //Disable the loading at CLDO input inside RF sub-system
    device_configCldo(DEVICE_SLEEP_ENTER_SLEEP);

    // Step 24 : Turn off MBS in RF
    DEVICE_SLEEP_ConfigRfMbs(false);

    // Step 25 : set KEEP_ACLB_CLOCKS_ON to 0 to disable ACLB clocks for SPI access
    DEVICE_SLEEP_ConfigAclbClk(false);
    
    // Step 26 : set bt_en_main_clk to 0 to disable BT main clock
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 &= (~0x00100000);  

    // Step 27 : change CLK source in CRU from POSC CLK to FRC CLK
    CRU_REGS->CRU_OSCCON &= (~0xf01);

    // Request oscillator switch to occur
    CRU_REGS->CRU_OSCCONSET = CRU_OSCCON_OSWEN_Msk;

    // Wait for indication of successful clock change before proceeding
    while(CRU_REGS->CRU_OSCCON & CRU_OSCCON_OSWEN_Msk);

    // If XTAL clock is OFF
    if ((CFG_REGS->CFG_CFGCON4 & 0x3000) == 0x2000)  // SOSC : XTAL_OFF
    {
        // Step 27.1 : If XTAL clock is OFF when bt_zb_subsys enters into sleep mode, 
        // set subsys_clk_src_sel to 1 via subsys config register (SUBSYS_CNTRL_REG1_ADDR[4]) to select PLL CLK as SRC clock
        BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG1 |= 0x10;
    
        // Step 28 : If XTAL clock is OFF when bt_zb_subsys enters into sleep mode, set BXTLEN to 0 via BT config register to disable XTAL
        device_Delay(4); // add 2us delay
        DEVICE_SLEEP_ConfigRfXtal(false);

        // Step 28.1 : If XTAL clock is OFF when bt_zb_subsys enters into sleep mode, set subsys_bypass_xtal_ready to 0 via subsys config register
        DEVICE_SLEEP_ConfigSubSysXtalReady(false);

    }
    // Step 29 : set deep sleep enable to 0
    DSCON_REGS->DSCON_DSCON &= ~(0x8000);

    // Step 30 : set sleep enable to 1, make CPU into sleep
    CRU_REGS->CRU_OSCCON |= 0x10;

    // Lock system since done with clock configuration
    devie_SysLock();
}

void DEVICE_ExitSleepMode(void)
{
    // unlock key sequence
    devie_SysUnlock();

    // step 1: Clear sleep flag
    RCON_REGS->RCON_RCON &= (~RCON_RCON_SLEEP_Msk);

    // If XTAL clock is off
    if ((CFG_REGS->CFG_CFGCON4 & 0x3000) == 0x2000) //SOSC : XTAL_OFF
    {
        
        // Step 2 : If XTAL clock is off when bt_zb_subsys enters into low power mode, wait for xtal_ready_out_sync
        // Enable bit 7 to creates one clk_lp_cycle wide pulse on ZBT Subsystem.external_NMI0 pin
        CFG_REGS->CFG_CFGCON1 |= CFG_CFGCON1_ZBTWKSYS_Msk;
        
        // Wait for xtal_ready      
        while(BTZB_XTAL_NOT_READY);

        // Step 2.1 :
        // If XTAL clock is OFF when bt_zb_subsys enters into sleep mode, 
        // set subsys_clk_src_sel to 0 via subsys config register (SUBSYS_CNTRL_REG1_ADDR[4]) to select XTAL CLK as SRC clock
        BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG1 &= (~0x10);
    }

    // Step 3 : Change CLK source in CRU from FRC CLK to POSC CLK
    CRU_REGS->CRU_OSCCON &= (~0xf01);
    CRU_REGS->CRU_OSCCON |= 0x200;

    // Request oscillator switch to occur
    CRU_REGS->CRU_OSCCONSET = CRU_OSCCON_OSWEN_Msk;

    // Wait for indication of successful clock change before proceeding
    while(CRU_REGS->CRU_OSCCON & CRU_OSCCON_OSWEN_Msk);

    // Step 4 : set bt_en_main_clk to 1 to enable BT main clock
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 |= 0x00100000;
    
    // Step 5 : set KEEP_ACLB_CLOCKS_ON to 1 via BT config register 
    DEVICE_SLEEP_ConfigAclbClk(true);
    
    // Step 6 : Turn on MBS in RF
    DEVICE_SLEEP_ConfigRfMbs(true);

    //Restore the setting of RF sub-system
    device_configCldo(DEVICE_SLEEP_EXIT_SLEEP);

    // Step 7 : Wait for MBS settling time. Settling time value is 35us
    device_Delay(4);
    
    // Step 8 : Set KEEP_ACLB_CLOCKS_ON to 0 via BT config register 
    DEVICE_SLEEP_ConfigAclbClk(false);

    // Step 9 : Assert external PLL power request
    CRU_REGS->CRU_SPLLCON &= ~(0x08);
       
    // Step 10 : Combining step 9, set EN_RFLDO_ovrd_en to 0 to enable CLKGEN LDO enable in RF 
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 &= (~0x8000);

    // Step 11 : Wait for LDO settling time. Settling time value is 10us
    device_Delay(1);
   
    // Step 12 : Set die_BENXOANA_ovrd_en to 0 to switch CLDO to LDO_PLL 
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG0 &= (~0x800);
    
    // Step 13 : Enable CLKGEN CLK enable in RF 
    DEVICE_SLEEP_ConfigRfClk(true);

    // Step 14 : Poll pll_lock_out_sync to wait until pll_lock_out_sync is set
    // wait for PLL Lock
    while(BTZB_PLL_NOT_LOCKED);

    // Step 15 : Restore REFOx registers programming for run mode

    // Check PMD lock bit
    if (CFG_REGS->CFG_CFGCON0 & CFG_CFGCON0_PMDLOCK_Msk)
    {
        // PMD lock is enabled, check CFGCLOCK
        if ((CFG_REGS->CFG_CFGCON0 & CFG_CFGCON0_CFGCLOCK_Msk) == 0)
        {
            // Disable PMD lock
            CFG_REGS->CFG_CFGCON0 &= ~CFG_CFGCON0_PMDLOCK_Msk;    
        }
    }

    // Restore all PMD setting
    device_configPmdReg(DEVICE_SLEEP_EXIT_SLEEP);

    //Restore the setting of REFOxCON register
    device_configRefOscReg(DEVICE_SLEEP_EXIT_SLEEP);

    // Configure ADC-CP Clock
    device_configAdcCpClk(DEVICE_SLEEP_EXIT_SLEEP);

    // Step 16 : Set PB1 CLK to SYS_CLK to restore its clock rate for run mode 
    CRU_REGS->CRU_PB1DIV = 0x8800; 

    // Step 17 : Restore PCHE Cache programming for run mode
    PCHE_REGS->PCHE_CHECON = 0x07000011;

    // Step 18 : Change CLK source in CRU from POSC CLK to SPLL1 CLK
    CRU_REGS->CRU_OSCCON &= (~0xf01);
    CRU_REGS->CRU_OSCCON |= 0x100;

    // Request oscillator switch to occur
    CRU_REGS->CRU_OSCCONSET = CRU_OSCCON_OSWEN_Msk;

    // Wait for indication of successful clock change before proceeding
    while(CRU_REGS->CRU_OSCCON & CRU_OSCCON_OSWEN_Msk);

    // Step 19 : Set subsys_clk_src_sel to 1 to change subsys clock source from XTAL CLK to PLL CLK
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG1 &= (~0x30);
    BTZBSYS_REGS->BTZBSYS_SUBSYS_CNTRL_REG1 |= 0x10;

    // Remove sleep enable
    // not match to word! word should have CRU_OSCCON
    CRU_REGS->CRU_OSCCON &= (~0x10); 

    // Lock system since done with clock configuration
    devie_SysLock();
}
