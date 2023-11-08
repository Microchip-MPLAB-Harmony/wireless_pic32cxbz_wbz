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

#ifndef __APPLICATION_H
#define __APPLICATION_H


#define IMG_MEM_TOPOLOGY_COUNT              2
#define FW_IMAGE_BLOCK_SIZE                 4096

#define METADATA_HEADER_SIZE                0x200
#define SLOT0_BASE_ADDR                     0x01000000
#if SOC_VER == BIGBUCK
  #define SLOT1_BASE_ADDR                   0x01080000
#else
  #define SLOT1_BASE_ADDR                   0x01040000
#endif

#define SLOT0_HEADER                        SLOT0_BASE_ADDR
#define SLOT0_FIRMWARE                      (SLOT0_BASE_ADDR + METADATA_HEADER_SIZE)

#define SLOT1_HEADER                        SLOT1_BASE_ADDR
#define SLOT1_FIRMWARE                      (SLOT1_BASE_ADDR + METADATA_HEADER_SIZE)

#define UNAUTH_FW_SIZE                      0xFFFFFFFF

#define READ_BLOCK_SZ               512
#define EXT_FLASH_HEADER_SZ         16

#define FLASH_PAGE_SIZE             4096

#define EXT_FLASH_HDR_SZ            (0x10)
#define EXT_FLASH_MAX_IMG_NUM       (2)
#define EXT_FLASH_START_ADDR        (0)
#define EXT_FLASH_MAX_IMG_SZ        (0x80000)

#define MANUFACTURE_ID              "MCHP"

#define Swap16(u16) ((uint16_t)(((uint16_t)(u16) >> 8) |\
                           ((uint16_t)(u16) << 8)))
#define Swap32(u32) ((uint32_t)(((uint32_t)Swap16((uint32_t)(u32) >> 16)) |\
                           ((uint32_t)Swap16((uint32_t)(u32)) << 16)))

typedef struct __attribute__((packed))
{
    uint32_t        MD_SEQ_NUM;
    uint8_t         MD_REV;
    uint8_t         MD_CONT_IDX;
    uint32_t        MD_COHERENCE;
    uint8_t         MD_AUTH_METHOD;
    uint8_t         MD_AUTH_KEY;
    uint8_t         MD_DEC_METHOD;
    uint8_t         MD_DEC_KEY;
    uint16_t        MD_PL_LEN;
    
    uint32_t        FW_IMG_REV;
    uint32_t        FW_IMG_SRC_ADDR;
    uint32_t        FW_IMG_DST_ADDR;
    uint32_t        FW_IMG_LEN;
    uint8_t         FW_IMG_AUTH_METHOD;
    uint8_t         FW_IMG_AUTH_KEY;
    uint8_t         FW_IMG_DEC_METHOD;
    uint8_t         FW_IMG_DEC_KEY;
    uint8_t         FW_IMG_SIG[96];
    uint8_t         MD_SIG[96];
} FW_IMG_HDR;

const void * GetTopologies(void);
const void * GetKeysSupported(void);


#define BOOT_ERROR_CRITICAL_FAILURE 0
#define critical_error(x)	while(1)

#endif


