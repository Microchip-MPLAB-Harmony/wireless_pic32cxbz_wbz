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

**************************************************************************** */
/** Descriptive File Name

  @Company
    Microchip Technology Inc.

  @File Name
    pta.c

  @Summary
    PTA GPIO Interface.

  @Description
    This file contains the source code of GPIO interface for PTA.
 */
/* ************************************************************************** */

/* ************************************************************************** */
/* ************************************************************************** */
/* Section: Included Files                                                    */
/* ************************************************************************** */
/* ************************************************************************** */

/* This section lists the other files that are included in this file.
 */

/* TODO:  Include other files here if needed. */
#include <stdbool.h>
#include "pta.h"
#include "definitions.h"

/* ************************************************************************** */
/* ************************************************************************** */
/* Section: File Scope or Global Data                                         */
/* ************************************************************************** */
/* ************************************************************************** */

volatile PtaIrqHandlerFunc_t gIrqHandler = NULL;

/* ************************************************************************** */
/* ************************************************************************** */
// Section: Local Functions                                                   */
/* ************************************************************************** */
/* ************************************************************************** */
// *****************************************************************************


bool PTA_ReqSet(PtaIrqHandlerFunc_t IrqHandler)
{
<#if PTA_INTERFACE == "3-Wire">
    PTA_REQ_Set();
</#if>
    gIrqHandler = (PtaIrqHandlerFunc_t)IrqHandler;
    return true;
}

void PTA_ReqClear(void)
{
    PTA_REQ_Clear();
}

bool PTA_PrioSet(void)
{
   PTA_PRIO_Set();
   return true;
}

void PTA_PrioClear(void)
{
    PTA_PRIO_Clear();
}

void PTA_ClearIrqHandler(void)
{
    gIrqHandler = NULL;
}

bool PTA_GetReq(void)
{
    if(NULL == gIrqHandler)
    {
        return false;
    }
    
    return true;
}

bool PTA_WlanStatus (void)
{
    if(0x1U == WLAN_ACTIVE_Get())
    {
        return true;
    }
    return false;
}

void PTA_WlanIrqCb (GPIO_PIN pin, uintptr_t context)
{
    taskENTER_CRITICAL();
    if((NULL != gIrqHandler) && (true == PTA_WlanStatus()))
    {
        gIrqHandler();
        gIrqHandler = NULL;
    }
    taskEXIT_CRITICAL();
}

void PTA_init(void)
{
    /* GPIO Initialization */
    GPIO_PinInterruptCallbackRegister(WLAN_ACTIVE_PIN, PTA_WlanIrqCb, 0);
    GPIO_PinIntEnable(WLAN_ACTIVE_PIN,GPIO_INTERRUPT_ON_RISING_EDGE);
}


/* *****************************************************************************
 End of File
 */
