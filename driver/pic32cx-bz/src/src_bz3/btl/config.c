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


#include "config.h"

#include "config/default/peripheral/nvm/plib_nvm.h"
#include "config/default/driver/sst26/drv_sst26.h"
#include "definitions.h"
#include "application.h"
#include "mem_interface.h"


/* Function:
    void Flash_Initialize(void)

  Description:
    This function initialize flash operation

  Input:
    None
  
  Return:
    None

  Remarks:
*/
void Flash_Initialize(void)
{
  NVM_Initialize();
}


/* Function:
    uint8_t Flash_WriteData(uint8_t *data, uint32_t addr, uint32_t rcount)

  Description:
    This function write data to eflash

  Input:
    data - pointer to the data to be written
    addr - the flash address that data writes to
    rcount - the amount to data to be written to flash
  
  Return:
    status to indicate if write operation successful

  Remarks:
*/
uint8_t Flash_WriteData(uint8_t *data, uint32_t addr, uint32_t rcount)
{
    bool written = false;
    int32_t count = (int32_t)rcount;
    
    // address must be 16 assigned
    addr &= 0xFFFFFFF0;
    count = (count%16 == 0) ? count:(count-count%16+16);
    
    while(count > 0)
    {
      if (false == NVM_IsBusy())
      {
        written = NVM_QuadWordWrite((uint32_t *)data, addr);
        if (written != true)
        {
            return 1;
        }
        else
        {
            data += 16;
            addr += 16;
            count -= 16;
        }
      }
    }
    
    return 0;
}


/* Function:
    uint8_t Flash_ReadData(bool fastRead, uint8_t *buffer, uint32_t addr, uint32_t count)

  Description:
    This function read data from flash to buffer in RAM

  Input:
    fastRead - boolean to indicate if invoking fast read, not used in this revision
    buffer - pointer to the buffer to hold the data which reads out
    addr - the flash address that data reads from
    count - the amount to data to be read from flash
  
  Return:
    status to indicate if read operation successful

  Remarks:
*/
uint8_t Flash_ReadData(bool fastRead, uint8_t *buffer, uint32_t addr, uint32_t count)
{
  NVM_Read( (uint32_t *)buffer, count, addr );
  return 0;
}


/* Function:
    uint8_t Flash_EraseSector(uint32_t addr, uint16_t pageCount)

  Description:
    This function erase data from specific flash address

  Input:
    addr - the flash address that data is to erased
    pageCount - the number of pages of flash data to be erased
  
  Return:
    status to indicate if erase operation successful

  Remarks:
*/
uint8_t Flash_EraseSector(uint32_t addr, uint16_t pageCount)
{
    uint8_t erased = 0;
    
    if ((addr % 0x1000) != 0)
    {
        return 2;
    }
    
    while (pageCount != 0)
    {
      if (false == NVM_IsBusy())
      {
        erased = NVM_PageErase(addr);
        if (erased == false)
        {
            return 1;
        }
        pageCount--;
        addr += 0x1000;
      }
    }
    
    return 0;  
}

/* Function:
    uint32_t Flash_ReadJedecId(void)

  Description:
    This function retrieved JedecID from the flash. It is not implemented 
    in this revision

  Input:
    None
  
  Return:
    Jedec ID that is read from flash

  Remarks:
*/
uint32_t Flash_ReadJedecId(void)
{
  return 0;
}

const IMG_MEM_INTERFACE flashInterface =
{
    Flash_Initialize,
    Flash_WriteData,
    Flash_ReadData,
    Flash_EraseSector,
    Flash_ReadJedecId
};


DRV_HANDLE sst26_handle = DRV_HANDLE_INVALID;


/* Function:
    void SST_Initialize(void)

  Description:
    This function initialize the driver before accessing SST external flash

  Input:
    None
  
  Return:
    None

  Remarks:
*/
void SST_Initialize(void)
{
  if( sst26_handle == DRV_HANDLE_INVALID)
  {
    sst26_handle = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
  }
}


/* Function:
    uint8_t SST_WriteData(uint8_t *data, uint32_t addr, uint32_t rcount)

  Description:
    This function write data to SST external flash

  Input:
    data - pointer to the data to be written
    addr - the SST flash address that data writes to
    rcount - the amount to data to be written to flash
  
  Return:
    status to indicate if write operation successful

  Remarks:
*/
uint8_t SST_WriteData(uint8_t *data, uint32_t addr, uint32_t rcount)
{
    bool written = false;
    int32_t count = (int32_t)rcount;
    
    // address must be 256 assigned
    addr &= 0xFFFFFF00;
    count = (count%256 == 0) ? count:(count-count%256+256);
    
    while(count > 0)
    {
      if (DRV_SST26_TransferStatusGet(sst26_handle) == DRV_SST26_TRANSFER_COMPLETED)
      {
        written = DRV_SST26_PageWrite( sst26_handle, (void *)data, addr );
        if (written != true)
        {
            return 1;
        }
        else
        {
            data += 256;
            addr += 256;
            count -= 256;
        }
      }
    }
    while(DRV_SST26_TransferStatusGet(sst26_handle) == DRV_SST26_TRANSFER_BUSY);
    return 0;
}

/* Function:
    uint8_t SST_ReadData(bool fastRead, uint8_t *buffer, uint32_t addr, uint32_t count)

  Description:
    This function read data from SST external flash to buffer in RAM

  Input:
    fastRead - boolean to indicate if invoking fast read, not used in this revision
    buffer - pointer to the buffer to hold the data which reads out
    addr - the SST external flash address that data reads from
    count - the amount to data to be read from flash
  
  Return:
    status to indicate if read operation successful

  Remarks:
*/
uint8_t SST_ReadData(bool fastRead, uint8_t *buffer, uint32_t addr, uint32_t count)
{
  bool status;

  while(DRV_SST26_TransferStatusGet(sst26_handle) == DRV_SST26_TRANSFER_BUSY);
  status = DRV_SST26_Read( sst26_handle, buffer, count, addr );
  
  if( status == false )
  {
    return 1;
  }
  return 0;
}

void __attribute__((optimize("-O0"))) delay(uint32_t d)
{
  uint32_t i;
  for(i = 0; i < d; i+=2) 
    i--; 
}

/* Function:
    uint8_t SST_EraseSector(uint32_t addr, uint16_t pageCount)

  Description:
    This function erase data from specific SST external flash address

  Input:
    addr - the SST external flash address that data is to erased
    pageCount - the number of pages of flash data to be erased
  
  Return:
    status to indicate if erase operation successful

  Remarks:
*/
uint8_t SST_EraseSector(uint32_t addr, uint16_t pageCount)
{
  bool status;
  while (pageCount != 0)
  {
    if(DRV_SST26_TransferStatusGet(sst26_handle) == DRV_SST26_TRANSFER_COMPLETED)
    {
      status = DRV_SST26_SectorErase( sst26_handle, addr );
      if (status == false)
      {
          return 1;
      }
      pageCount--;
      addr += 0x1000;
      
      // Introduce a manual delay, otherwise, the erase operation
      // could not complete for the 2nd block
      delay(0x30000);
    }
  }
  while(DRV_SST26_TransferStatusGet(sst26_handle) == DRV_SST26_TRANSFER_BUSY);
  return 0;
}

/* Function:
    uint32_t SST_ReadJedecId(void)

  Description:
    This function retrieved JedecID from the SST external flash. 

  Input:
    None
  
  Return:
    Jedec ID that is read from SST external flash

  Remarks:
*/
uint32_t SST_ReadJedecId(void)
{
  bool status;
  uint32_t jedec_id;
  
  status = DRV_SST26_ReadJedecId(sst26_handle, &jedec_id);
  if( status )
  {
    return jedec_id;
  }
  return 0;
}

const IMG_MEM_INTERFACE sst26Interface = 
{
  SST_Initialize,
  SST_WriteData,
  SST_ReadData,
  SST_EraseSector,
  SST_ReadJedecId
};


const SLOT_PARAMS slots512kFlash[2] = {

    {
        0x01000000,
        {0x40000, 0x80000},
        true
    },
    {
        0x01040000,
        {0x40000, 0},
        true
    }
};

const SLOT_PARAMS slotsSST26Flash[2] = {

    {
        0x00000000,
        {0x80000, 0},
        false
    },
    {
        0x00080000,
        {0x80000, 0},
        false
    },
};


//const uint32_t devId2MFlash = 0x09C60053;
//const uint32_t devId1MFlash = 0x09C40053;
//const uint32_t devIdEon512kFlash = 0x09C30053;
//const uint32_t devIdSST512kFlash = 0x09C20053;

const IMG_MEM_TOPOLOGY imgMems[IMG_MEM_TOPOLOGY_COUNT] =
{
    // 512KB Internal flash
    {
        .u16ErasePageSz = 4096,
        .u16ProgRowSz = 1024,
        .u32UmmAddrStart = 0x01000000,
        .u32TotSize = 0x0007FFFF,
        .u8SlotCount = 2,
        .pSlots = &slots512kFlash[0],
        .u32CalIdx = 0x7FFFF,
        .ifFlash = &flashInterface,
        .u8DevIdCount = 0x00,
        .pDevIds = NULL,
        .u32DevIdMask = 0x00000000,
        .u32AddrPosMask = 0x01000000,
        .u32AddrNegMask = 0x0107FFFF,
        .u32BlankCheck = 0xFFFFFFFF
    },
    // SST26 external flash
    {
        .u16ErasePageSz = 4096,
        .u16ProgRowSz = 256,
        .u32UmmAddrStart = 0x00000000,
        .u32TotSize = 0x007FFFFF,
        .u8SlotCount = 2,
        .pSlots = &slotsSST26Flash[0],
        .u32CalIdx = 0x7FFFFF,
        .ifFlash = &sst26Interface,
        .u8DevIdCount = 0x00,
        .pDevIds = NULL,
        .u32DevIdMask = 0x00000000,
        .u32AddrPosMask = 0x00000000,
        .u32AddrNegMask = 0x007FFFFF,
        .u32BlankCheck = 0xFFFFFFFF
    }
    /*
    // 1 MB Flashes
    {
        .u16ErasePageSz = 4096,
        .u16ProgRowSz = 1024,
        .u32UmmAddrStart = 0x1000000,
        .u32TotSize = 0x100000,
        .u8SlotCount = 2,
        .pSlots = &slots1MFlash[0],
        .u32CalIdx = 0xF00000,
        .ifFlash = &flashInterface,
        .u8DevIdCount = 1,
        .pDevIds = &devId1MFlash,
        .u32DevIdMask = 0xFFFF0FFE,
        .u32AddrPosMask = 0x00000000,
        .u32AddrNegMask = 0x0FFFFFFF,
        .u32BlankCheck = 0xFFFFFFFF                
    },*/
};

typedef enum
{
    AUTH_METHOD_NONE = 0,
    AUTH_METHOD_CRC16 = 1,
    AUTH_METHOD_ECDSA_P256 = 2,
    AUTH_METHOD_ECDSA_P384 = 3,
    AUTH_METHOD_MAX = 4
} AUTH_METHODS;

typedef enum
{
    DEC_METHOD_NONE = 0
} DEC_METHODS;


const uint8_t validAuthMethods[] = {(uint8_t) AUTH_METHOD_ECDSA_P384, (uint8_t) AUTH_METHOD_ECDSA_P256, (uint8_t) AUTH_METHOD_NONE} ;
const uint8_t validDecMethods = (uint8_t) DEC_METHOD_NONE;
const uint8_t validKeyIndex = 0;

const KEYS_SUPPORTED validKeyTypes =
{
    .mdAuthKeyMethodCount  = 3,
    .mdAuthKeyMethods = &validAuthMethods[0],
    .mdAuthKeyIndexCount = 1,
    .mdAuthKeyIndicies = &validKeyIndex,

    .mdDecKeyMethodCount = 1,
    .mdDecKeyMethods = &validDecMethods,
    .mdDecKeyIndexCount = 1,
    .mdDecKeyIndicies = &validKeyIndex,

    .fwAuthKeyMethodCount  = 3,
    .fwAuthKeyMethods = &validAuthMethods[0],
    .fwAuthKeyIndexCount = 1,
    .fwAuthKeyIndicies = &validKeyIndex,

    .fwDecKeyMethodCount = 1,
    .fwDecKeyMethods = &validDecMethods,
    .fwDecKeyIndexCount = 1,
    .fwDecKeyIndicies = &validKeyIndex,
};

/* Function:
    const void * GetTopologies(void)

  Description:
    This function get list of topologies supported in this device

  Input:
    None
  
  Return:
    Pointer to the list of supported topologies
*/
const void * GetTopologies(void)
{
    return &imgMems[0];
}

/* Function:
    const void * GetKeysSupported(void)

  Description:
    This function get list of key types supported in this device

  Input:
    None
  
  Return:
    Pointer to the list of supported key types

  Remarks:
*/
const void * GetKeysSupported(void)
{
    return &validKeyTypes;
}

