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
#include "definitions.h"
#include "dfu/pe/include/uart.h"
//#include "configuration.h"



volatile uint8_t data_avail = 0;

void uart_cb(SERCOM_USART_EVENT event, uintptr_t context)
{
  // If RX data from UART reached threshold (previously set to 1)
  if( event == SERCOM_USART_EVENT_READ_THRESHOLD_REACHED )
  {
    data_avail = 1;
  }
}

void UART_Init( void )
{
  // Enable UART Read
  SERCOM0_USART_ReadNotificationEnable(true, true);
  // Set UART RX notification threshold to be 1
  SERCOM0_USART_ReadThresholdSet(1);
  // Register the UART RX callback function
  SERCOM0_USART_ReadCallbackRegister(uart_cb, (uintptr_t)NULL);
}

static UART_ERROR UART_ErrorGet( void )
{
    return SERCOM0_USART_ErrorGet();
}

uint32_t UART_Read(uint8_t *rb, const uint32_t len, const int32_t wait)
{
    uint32_t count=0;
    uint32_t timeout;
    
    UART_ErrorGet(); //clear errors 
    for (;count < len; count++)
    {
        for (timeout=0; (data_avail==0)&&(timeout <= wait); timeout++)
            ;
        if (timeout > wait)
            return count;
        SERCOM0_USART_Read(rb, 1);
        data_avail = 0;
        rb++;
    }
    
    return count;
}


void UART_Write(int8_t *wb, uint32_t len)
{
    SERCOM0_USART_Write((uint8_t *)wb, len);
}


