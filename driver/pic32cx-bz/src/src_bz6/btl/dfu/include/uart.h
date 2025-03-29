/* 
 * File:   uart.h
 * Author: C21319
 *
 * Created on October 12, 2020, 1:59 PM
 */

#ifndef UART_H
#define	UART_H

#ifdef	__cplusplus
extern "C" {
#endif
//#include <xc.h>

#define UART_RXFIFO_DEPTH       9   
    
typedef enum
{
    UART_ERROR_NONE = 0,
    UART_ERROR_OVERRUN = 0x02,
    UART_ERROR_FRAMING = 0x04,
    UART_ERROR_PARITY  = 0x08

} UART_ERROR;


extern void UART_Init(void);
extern uint32_t UART_Read(uint8_t *rb, const uint32_t len, const int32_t wait);
extern void UART_Write(int8_t *wb, uint32_t len);

#ifdef	__cplusplus
}
#endif

#endif	/* UART_H */

