/*********************************************************************
 *
 *                  Flash Programming Executive header file
 *
 *********************************************************************
 * FileName:        progexec.h
 * Dependencies:
 * Processor:       Daytona
 * 
 * Complier:        MPLAB C30 v1.31.00 or higher
 *                  MPLAB IDE v7.22.00 or higher
 * Company:         Microchip Technology, Inc.
 *
 * Software License Agreement
 *
 * The software supplied herewith by Microchip Technology Incorporated
 * (the �Company�) for its PICmicro� Microcontroller is intended and
 * supplied to you, the Company�s customer, for use solely and
 * exclusively on Microchip PICmicro Microcontroller products. The
 * software is owned by the Company and/or its supplier, and is
 * protected under applicable copyright laws. All rights are reserved.
 * Any use in violation of the foregoing restrictions may subject the
 * user to criminal sanctions under applicable laws, as well as to
 * civil liability for the breach of the terms and conditions of this
 * license.
 *
 * THIS SOFTWARE IS PROVIDED IN AN �AS IS� CONDITION. NO WARRANTIES,
 * WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT LIMITED
 * TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 * PARTICULAR PURPOSE APPLY TO THIS SOFTWARE. THE COMPANY SHALL NOT,
 * IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR
 * CONSEQUENTIAL DAMAGES, FOR ANY REASON WHATSOEVER.
 *
 *********************************************************************
 *
 * $Id$
 *
 ********************************************************************/
#include <stdint.h> 
#include <stdbool.h>
#include "crc.h"

#ifndef __progexec_h__
#define __progexec_h__

/* Program Executive Version Number */
#define PROG_EXEC_VERSION_NUMBER    0x1
#define PROG_EXEC_VNUM_IDENTIFIER   0xCDAB

/* SRAM data area */
#define PE_CMD_SRAM_ADDR            0xA00AFFF0
#define PE_RESP_SRAM_ADDR           0xA00AFFFC

#define PE_CMD_PAYLOAD_SIZE         4096
#define PE_CMD_MAX_HEADER           16     
#define PE_CMD_SIZE                 (PE_CMD_PAYLOAD_SIZE + \
                                     PE_CMD_MAX_HEADER)

#define PE_CMD_TIMEOUT              10000
#define PE_RESP_SIZE                0x4

#define PE_DEVICEID(x)              x //(( (x>>12) & 0xFF ))

#define CMD(x)          ((x>>16))      /* extract command */
#define LEN(x)          ((x&0xFFFF))   /* extract length */

#define ROW_SIZE        128

/* Command Packet Structure */
typedef struct {
   
/* command values */
#define PROG_ROW_CMD            0x0
#define READ_CMD                0x1
#define PROGRAM_CMD             0x2
#define PROG_WORD_CMD           0x3
#define CHIP_ERASE_CMD          0x4
#define PAGE_ERASE_CMD          0x5
#define BLANK_CHECK_CMD         0x6
#define EXEC_VERSION_CMD        0x7
#define GET_CRC_CMD             0x8
#define PROGRAM_CLUSTER_CMD     0x9
#define GET_DEVICEID            0xA
#define CHANGE_CFG_CMD          0xB
#define GET_CHECKSUM_CMD        0xC
#define PROG_QUAD_WORD_CMD      0xD
#define PROG_DBL_WORD_CMD       0xE
#define PROG_QUAD_DWORD_CMD     0x10
#define PROG_CLUSTER_VERIFY_CMD 0x11
#define PE_TEST                 0xF /* general purpose test command */

/* Image cluster verification methods */    
#define PE_CFG_CHECKSUM         0x1
#define PE_CFG_CRC              0x2           
    
    uint16_t cmd;
    uint16_t operand;
   
   /* command specific data */
    union 
    {      
        /* general purpose generic */
        struct 
        {
            uint32_t data1;
            uint32_t data2;
        } generic;

       struct
       {
            void *addr;
            uint32_t len;
            uint32_t checksum;  
            void *payload;
          /* data of variable length to follow */
       } progClusterVerify;      

       /* erase page */
       struct
       {
            void *addr;
            uint32_t reserved;
       } erasePage;
       
       /* erase Chip */
       struct
       {
            void *addr;
            uint32_t reserved;
       } eraseChip;       

            /* verify */
       struct
       {
            void *addr;
            uint32_t len;         
            uint32_t reserved;
       } blanckCheck;
    };  
} FPP_CMD_PACKET, *PFPP_CMD_PACKET;

/* Response Packet Structure */
typedef struct {
   
   uint16_t lastCmd;
   
/* error code values */
#define PASS_RESP    0x00
#define FAIL_RESP    0x02
#define NACK_RESP    0x03
   uint16_t errCode;

} FPP_RESP_PACKET, *PFPP_RESP_PACKET;

#endif /* __progexec_h__ */
