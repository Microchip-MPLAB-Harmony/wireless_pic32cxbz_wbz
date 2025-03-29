// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2024 Microchip Technology Inc. and its subsidiaries.
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

/* ************************************************************************** */
/** Descriptive File Name

  @Company
    Microchip Technology Inc.

  @File Name
    pta.h

  @Summary
    PTA GPIO Interface.

  @Description
    This file provides API references of PTA GPIO interface.
 */
/* ************************************************************************** */

#ifndef _PTA_H    /* Guard against multiple inclusion */
#define _PTA_H


/* ************************************************************************** */
/* ************************************************************************** */
/* Section: Included Files                                                    */
/* ************************************************************************** */
/* ************************************************************************** */
#include "peripheral/gpio/plib_gpio.h"

/* This section lists the other files that are included in this file.
 */

/* TODO:  Include other files here if needed. */


/* Provide C++ Compatibility */
#ifdef __cplusplus
extern "C" {
#endif

// *****************************************************************************
// *****************************************************************************
// Section: Types
// *****************************************************************************
// *****************************************************************************

typedef void (* PtaIrqHandlerFunc_t)(void);
/* ************************************************************************** */
    /*
  Function:
    void PTA_init(void)

  Summary:
     Initializes the PTA GPIO Interface

  Description:
    This function initializes the PTA GPIO Interfaces and registers the Callback.

  Precondition:
    None

  Parameters:
   None

  Returns:
    None

  Example:
    <code>
     PTA_init();
    </code>

  Remarks:
     This function ideally needs to called during SYS_Initialize()
*/
void PTA_init(void);

// *****************************************************************************
/*
  Function:
    bool PTA_ReqSet(PtaIrqHandlerFunc_t *)

  Summary:
    Asserts the PTA Request line  

  Description:
    This function asserts the PTA Request Signal. 

  Precondition:
    PTA_init() should have been called before calling this function.

  Parameters:
    PtaIrqHandlerFunc_t - A function pointer to the IRQ handler. This function 
                          pointer will be called when WLAN IRQ is received.

  Returns:
    True - if the PTA_ReqSet is successful
    False - if the PTA_ReqSet is unsuccessful

  Example:
    <code>
    if(PAL_PTA_ReqSet(BT_SYS_PtaWlanActiveIrqHandler))
    {
        // code here
    }
    </code>

  Remarks:
     This function asserts PTA pin and stores the IRQ handler function pointer.
     This routine will be called from the stack.
*/
bool PTA_ReqSet(PtaIrqHandlerFunc_t );

// *****************************************************************************
/*
  Function:
    void PTA_ReqClear(void)

  Summary:
    De-asserts the PTA Req

  Description:
    This function de-asserts the PTA Request Signal. 

  Precondition:
    None

  Parameters:
    None

  Returns:
    None

  Example:
    <code>
    PTA_ReqClear();
    </code>

  Remarks:
    This routine will be called from the stack. 
*/
void PTA_ReqClear(void);

// *****************************************************************************
/*
  Function:
    bool PTA_PrioSet(void)

  Summary:
    Asserts the PTA Priority line  

  Description:
    This function asserts the PTA Priority Signal.

  Precondition:
    None

  Parameters:
    None

  Returns:
    True - if the PTA_PrioSet is successful
    False - if the PTA_PrioSet is unsuccessful

  Example:
    <code>
    if(PTA_PrioSet())
    {
        // code here
    }
        
    </code>

  Remarks:
    This routine will be called from the stack. 
*/
bool PTA_PrioSet(void);

// *****************************************************************************
/*
  Function:
    void PTA_PrioClear(void)

  Summary:
    De-asserts the PTA Priority line

  Description:
    This function de-asserts the PTA Priority Signal.

  Precondition:
    None

  Parameters:
    None

  Returns:
    None

  Example:
    <code>
    PTA_PrioClear();
    </code>

  Remarks:
    This routine will be called from the stack. 
*/
void PTA_PrioClear(void);

// *****************************************************************************
/*
  Function:
    void PTA_ClearIrqHandler(void)

  Summary:
    CLear the PTA Irq Handler registered  

  Description:
    This function clears the PTA Irq Handler registered.

  Precondition:
    None

  Parameters:
    None

  Returns:
    None

  Example:
    <code>
    PTA_ClearIrqHandler();
        
    </code>

  Remarks:
    This routine will be called from the stack. 
*/
void PTA_ClearIrqHandler(void);

// *****************************************************************************
/*
  Function:
    bool PTA_GetReq(void)

  Summary:
    Gets the status of Ongoing PTA Request  

  Description:
    This function gets the status of Ongoing PTA Request.

  Precondition:
    None

  Parameters:
    None

  Returns:
    True - if there is no Ongoing PTA Request 
    False - if there is a Ongoing PTA Request

  Example:
    <code>
    if(PTA_GetReq())
    {
        
    }
    </code>

  Remarks:
    This routine will be called from the stack. 
*/
bool PTA_GetReq(void);

// *****************************************************************************
/*
  Function:
    bool PTA_WlanStatus(void)

  Summary:
    Gets the WLAN Active Signal Status

  Description:
    This function returns the WLAN Active Signal Status.

  Precondition:
    None

  Parameters:
    None

  Returns:
    PTA_WlanStatus - True  - If Signal is Active high.
            - False - If Signal is Active low.

  Example:
    <code>
    PTA_WlanStatus wlanStatus;
    wlanStatus = PTA_WlanStatus();
    if(wlanStatus)
    {
      // Do required  
    }
    </code>

  Remarks:
    This routine will be called from the stack.
*/
bool PTA_WlanStatus (void);

// *****************************************************************************
/*
  Function:
	void PTA_WlanIrqCb(GPIO_PIN pin, uintptr_t context)

  Summary:
    This is callback function registered with WLAN_STATUS input pin.

  Description:
    This function will be called when WLAN_STATUS input pin interrupted.

  Precondition:
    None

  Parameters:
    None

  Returns:
    None

  Example:
    <code>
    GPIO_PinInterruptCallbackRegister(WLAN_ACTIVE_PIN, PTA_WlanIrqCb, 0);
    </code>

  Remarks:
    This routine will be called from GPIO handler.
*/
void PTA_WlanIrqCb (GPIO_PIN pin, uintptr_t context);



    /* Provide C++ Compatibility */
#ifdef __cplusplus
}
#endif

#endif /* _PTA_H */

/* *****************************************************************************
 End of File
 */
