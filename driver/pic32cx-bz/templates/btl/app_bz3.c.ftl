/*******************************************************************************
  MPLAB Harmony Application Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app.c

  Summary:
    This file contains the source code for the MPLAB Harmony application.

  Description:
    This file contains the source code for the MPLAB Harmony application.  It
    implements the logic of the application's state machine and it may call
    API routines of other MPLAB Harmony modules in the system, such as drivers,
    system services, and middleware.  However, it does not call any of the
    system interfaces (such as the "Initialize" and "Tasks" functions) of any of
    the modules in the system or make any assumptions about when those functions
    are called.  That is the responsibility of the configuration-specific system
    files.
 *******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include "config.h"
#include "mem_interface.h"
#include "dfu/dfu.h"
#include "application.h"
#include "app.h"


#include "security.h"

extern DRV_HANDLE sst26_hdl;
extern const SLOT_PARAMS slots512kFlash[];
extern bool restore_sercom0_hs;

extern void Flash_Initialize(void);
extern uint8_t Flash_WriteData(uint8_t *data, uint32_t addr, uint32_t rcount);
extern uint8_t Flash_ReadData(bool fastRead, uint8_t *buffer, uint32_t addr, uint32_t count);
extern uint8_t Flash_EraseSector(uint32_t addr, uint16_t pageCount);
extern void delay(uint32_t value);

bool saveEncryptedHash(FW_IMG_HDR *p_header, uint32_t img_address);

// *****************************************************************************
// *****************************************************************************
// Section: Global Data Definitions
// *****************************************************************************
// *****************************************************************************

// *****************************************************************************
/* Application Data

  Summary:
    Holds application data

  Description:
    This structure holds the application's data.

  Remarks:
    This structure should be initialized by the APP_Initialize function.

    Application strings and buffers are be defined outside this structure.
*/

APP_DATA appData;





// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************

/* TODO:  Add any necessary callback functions.
*/

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************


/* TODO:  Add any necessary local functions.
*/

void SERCOM0_USART_deInit(void)
{
  SERCOM0_REGS->USART_INT.SERCOM_CTRLA = 0;
  SERCOM0_REGS->USART_INT.SERCOM_BAUD = 0;
  SERCOM0_REGS->USART_INT.SERCOM_CTRLB = 0;
  
  /* Wait for sync */
  while((SERCOM0_REGS->USART_INT.SERCOM_SYNCBUSY) != 0U)
  {
      /* Do nothing */
  }
  
  SERCOM0_REGS->USART_INT.SERCOM_INTENCLR = 0xBF;
  SERCOM0_REGS->USART_INT.SERCOM_INTFLAG = 0;  
}

void NVIC_deInit(void)
{
  NVIC_DisableIRQ(NVM_IRQn);
  NVIC_DisableIRQ(SERCOM0_IRQn);
  NVIC_DisableIRQ(TC3_IRQn);
}


void IMG_MEM_FindValidTopologies(DEVICE_CONTEXT * ctx)
{
    uint32_t i = 0;
    uint32_t j = 0;
    IMG_MEM_TOPOLOGY * imgMems = (IMG_MEM_TOPOLOGY *)GetTopologies();
    
    ctx->topologyCount = 0x00;
    
    for (i = 0; i < IMG_MEM_TOPOLOGY_COUNT; i++)
    {
      if (j == MAX_MEM_TOPOLOGIES)
      {
          critical_error(BOOT_ERROR_CRITICAL_FAILURE);
          critical_error(BOOT_ERROR_CRITICAL_FAILURE);
      }
      ctx->validTops[j++] = &imgMems[i];
      ctx->topologyCount++;
    }
}

void print_buf(uint8_t *buf, const size_t size)
{
    SERCOM0_USART_Write(buf, size);
}

void start_dfu(void)
{
  DEVICE_CONTEXT ctx;
  
  IMG_MEM_FindValidTopologies(&ctx);
  if (ctx.validTops[0] != NULL)
  {
    dfu(ctx.validTops, ctx.topologyCount);
  }
}

void ApplicationTransition(uint32_t APP_START_ADDRESS)
{
    //stack pointer
    uint32_t msp            = *(uint32_t *)(APP_START_ADDRESS);
    //application reset_vector
    uint32_t reset_vector   = *(uint32_t *)(APP_START_ADDRESS + 4);

    // delay to make sure all UART output finish, could remove if no UART output
    delay(0x30000); 
    
    /* Disable the USART before configurations */
    SERCOM0_REGS->USART_INT.SERCOM_CTRLA &= ~SERCOM_USART_INT_CTRLA_ENABLE_Msk;
    if( restore_sercom0_hs )
    {
      CFG_REGS->CFG_CFGCON1CLR = CFG_CFGCON1_SCOM0_HSEN(1);
    }
    
    /* Wait for sync */
    while((SERCOM0_REGS->USART_INT.SERCOM_SYNCBUSY) != 0U)
    {
        /* Do nothing */
    }

    // disable silex engine
    SILEX_REGS->SILEX_CRYPTOCON = 0x00;
    
    //load the stack pointer
    if (msp == 0xffffffff)
    {
        return;
    }
    __set_MSP(msp);
    //jump to application's reset_vector
    asm("bx %0"::"r" (reset_vector));
}

bool checkImgHeader(FW_IMG_HDR *img_header)
{
  uint32_t coherence;
  bool status;
  
  coherence = Swap32(img_header->MD_COHERENCE);
  if (rom_memcmp((uint8_t *)&coherence, (uint8_t *)MANUFACTURE_ID, 4) != 0)
  {
    return false;
  }
  status = validMetaHeader(img_header);
  if( status == false )
  {
    return false;
  }
  return true;
}

uint32_t minimum_seq(uint8_t *chosen_slot)
{
  uint8_t i;
  uint32_t seq_num;
  FW_IMG_HDR header;
  bool status;
  
  seq_num = 0xFFFFFFFF;
  *chosen_slot = 0xFF;
  for(i = 0; i < 2; i++)
  {
    rom_memcpy((uint8_t *)&header, (uint8_t *)(slots512kFlash[i].hdrOffset), sizeof(FW_IMG_HDR));
    status = checkImgHeader(&header);
    if( status )
    {
      if( header.MD_SEQ_NUM < seq_num )
      {
        seq_num = header.MD_SEQ_NUM;
        *chosen_slot = i;
      }
    }
  }
  return seq_num;
}


bool CopyFlashImage(uint32_t saddr, uint8_t encryption, uint16_t crc16, bool external, bool ext_hdr)
{
  uint8_t plain[READ_BLOCK_SZ];
  uint8_t secured[READ_BLOCK_SZ];
  uint8_t next_iv[AES_BLOCK_SZ];
  FW_IMG_HDR img_header, int_header;
  bool status;
  uint16_t blocks, block_sz, i;
  uint32_t taddr, seq_num;
  uint8_t int_status;
  uint16_t cal_crc16;
  
  if( external )
  {
    sst26_hdl = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
    if( DRV_HANDLE_INVALID == sst26_hdl )
    {
      return false;
    }
  }
  
  if( encryption )
  {
    if( external )
    {
      status = DRV_SST26_Read(sst26_hdl, secured, READ_BLOCK_SZ, saddr);
      if( status == false )
      {
        return false;
      }
    }
    else
    {
      rom_memcpy(secured, (uint8_t *)saddr, READ_BLOCK_SZ);
    }
    rom_memcpy(next_iv, &secured[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
    status = aes_cbc_decrpyt(secured, plain, READ_BLOCK_SZ, (uint8_t *)aes_iv);
    if( status == false )
    {
      return false;
    }
  }
  else
  {
    if( external )
    {
      status = DRV_SST26_Read(sst26_hdl, plain, sizeof(FW_IMG_HDR), saddr);
      if( status == false )
      {
        return false;
      }
    }
    else
    {
      rom_memcpy(plain, (uint8_t *)saddr, sizeof(FW_IMG_HDR));
    }
  }
  
  rom_memcpy((uint8_t *)&img_header, plain, sizeof(FW_IMG_HDR));
  
  status = checkImgHeader(&img_header);
  if( status == false )
  {
    return false;
  }

  Flash_Initialize();
  taddr = slots512kFlash[0].hdrOffset;
  rom_memcpy((uint8_t *)&int_header, (uint8_t *)(slots512kFlash[0].hdrOffset), sizeof(FW_IMG_HDR));
  status = checkImgHeader(&int_header);
  if( status )
  {
    seq_num = int_header.MD_SEQ_NUM;
  }
  else
  {
    seq_num = 0xFFFFFFFF;
  }
    
  // erase flash
  blocks = (img_header.FW_IMG_LEN+METADATA_HEADER_SIZE)/FLASH_PAGE_SIZE;
  if( (img_header.FW_IMG_LEN+METADATA_HEADER_SIZE) % FLASH_PAGE_SIZE > 0 )
  {
    blocks++;
  }
  int_status = Flash_EraseSector(taddr, blocks);
  if( int_status != 0 )
  {
    return false;
  }
  
  blocks = img_header.FW_IMG_LEN / READ_BLOCK_SZ;
  if( (img_header.FW_IMG_LEN % READ_BLOCK_SZ) > 0 )
  {
    blocks++;
  }
  for(i = 0; i < blocks; i++)
  {
    if( (i < blocks-1) || (img_header.FW_IMG_LEN%READ_BLOCK_SZ==0) )
    {
      block_sz = READ_BLOCK_SZ;
    }
    else
    {
      block_sz = img_header.FW_IMG_LEN%READ_BLOCK_SZ;
    }
    if( encryption )
    {
      if( external )
      {
        status = DRV_SST26_Read(sst26_hdl, secured, block_sz, saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ);
        if( status == false )
        {
          return false;
        }
      }
      else
      {
        rom_memcpy(secured, (uint8_t *)(saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ), block_sz);
      }
      status = aes_cbc_decrpyt(secured, plain, block_sz, next_iv);
      if( status == false )
      {
        return false;
      }
      rom_memcpy(next_iv, &secured[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
    }
    else
    {
      if( external )
      {
        status = DRV_SST26_Read(sst26_hdl, plain, block_sz, saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ);
        if( status == false )
        {
          return false;
        }
      }
      else
      {
        rom_memcpy(plain, (uint8_t *)(saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ), block_sz);
      }
    }
    
    int_status = Flash_WriteData(plain, taddr+METADATA_HEADER_SIZE+i*READ_BLOCK_SZ, block_sz);
    if( int_status != 0 )
    {
      return false;
    }
  }

  img_header.FW_IMG_SRC_ADDR = taddr+METADATA_HEADER_SIZE;
  img_header.MD_SEQ_NUM = seq_num - 1; // 0xFFFFFFFF;
  rom_memset(plain, 0, METADATA_HEADER_SIZE);
  rom_memcpy((uint8_t *) plain, (uint8_t *)&img_header, sizeof (FW_IMG_HDR));
  int_status = Flash_WriteData(plain, taddr, METADATA_HEADER_SIZE);
  
  if( (ext_hdr == false) && (external == false) )
  {
    crc16 = get_crc16(saddr, false, false);
  }
  cal_crc16 = 0;
  cal_crc16 = get_crc16(taddr, false, false);

  if( cal_crc16 != crc16 )
  {
    DRV_SST26_Close(sst26_hdl);
    sst26_hdl = DRV_HANDLE_INVALID;
    return false;
  }
  if( external )
  {
    print_buf((uint8_t *)"Copied Image from Ext to Internal Flash\r\n", 41);
  }
  else
  {
    print_buf((uint8_t *)"Copied Image from Internal Slot 1 to Slot 0\r\n", 45);
  }
  
  if( ext_hdr )
  {
    EXT_FLASH_HEADER extf_header;
    
    if( external )
    {
      status = DRV_SST26_Read(sst26_hdl, &extf_header, EXT_FLASH_HEADER_SZ, (saddr&0xFFFFFF00));
      if( status == false )
      {
        return false;
      }
      extf_header.seq_num = seq_num-1;
      status = DRV_SST26_Read(sst26_hdl, &plain[sizeof(EXT_FLASH_HEADER)], (256-sizeof(EXT_FLASH_HEADER)), saddr);
      rom_memcpy(plain, (uint8_t *)&extf_header, sizeof(EXT_FLASH_HEADER));
      int_status = DRV_SST26_PageWrite( sst26_hdl, (void *)plain, (saddr&0xFFFFFF00));
      while(DRV_SST26_TransferStatusGet(sst26_hdl) == DRV_SST26_TRANSFER_BUSY);
    }
    else
    {
      // have to erase the image because of possible ECC bus error by not writing to the complete row
      int_status = Flash_EraseSector((saddr&0xFFFFF000), 1);
    }
  }
  else if( external == false )
  {
    Flash_EraseSector((saddr&0xFFFFF000), 1);
  }
  
  if( external )
  {
    DRV_SST26_Close(sst26_hdl);
    sst26_hdl = DRV_HANDLE_INVALID;
  }
  
  status = saveEncryptedHash(&img_header, (taddr+METADATA_HEADER_SIZE));
  if( status )
  {
    print_buf((uint8_t *)"Saved Secured Hash\r\n", 20);
  }
  print_buf((uint8_t *)"Jump to App\r\n", 13);
  ApplicationTransition(taddr+METADATA_HEADER_SIZE);
  return true;
}




static bool GenerateHash(uint8_t hash_sz, uint8_t *data, uint32_t len, uint8_t *digest)
{
  struct sxhash imgHashCtx;
  int r;
  
  rom_memset (digest, 0x00, 64);    
  rom_memset ((uint8_t *)&imgHashCtx, 0x00, sizeof(struct sxhash)); 
  
  if(hash_sz == 32)
  {
      r = SX_HASH_CREATE_SHA256(&imgHashCtx, sizeof(struct sxhash));
  } 
  else
  {
      r = SX_HASH_CREATE_SHA384(&imgHashCtx, sizeof(struct sxhash));
  }

  if (r != SX_OK)
  {
      return false;
  }

  r = SX_HASH_FEED(&imgHashCtx, (const char *)data, len);
  if (r != SX_OK)
  {
      return false;
  }
  
  r = SX_HASH_DIGEST((struct sxhash *)&imgHashCtx, (char *) digest);

  if (r != SX_OK)
  {
      return false;
  }

  do
  {
      r = SX_HASH_STATUS(&imgHashCtx);
  } while (r == SX_ERR_HW_PROCESSING);

  if (r != SX_OK)
  {
      return false;
  }
  
  return true;
}

static bool EncryptHash(uint8_t *input, uint32_t size, uint8_t *output)
{
  struct sxblkcipher cipher;
  struct sxkeyref key1;
  int status;
  
  key1 = SX_KEYREF_LOAD_BY_ID(0);
  status = SX_BLKCIPHER_CREATE_AESECB_ENC(&cipher, (const struct sxkeyref *)&key1);
  if( status != SX_OK )
  {
    return false;
  }
  
  status = SX_BLKCIPHER_CRYPT(&cipher, (const char*)input, size, (char *)output);
  if (status != SX_OK )
  {
    return false;
  }
  
  status = SX_BLKCIPHER_RUN(&cipher);
  if (status != SX_OK )
  {
    return false;
  }

  status = SX_BLKCIPHER_WAIT(&cipher);
  if (status != SX_OK )
  {
    return false;
  }

  return true;
}


bool getEncryptedHash(FW_IMG_HDR *p_header, uint32_t img_address, uint8_t *sdigest)
{
  uint8_t digest[64] __attribute__((__aligned__(64)));
  uint8_t hash_sz;
  
  if( p_header->MD_AUTH_METHOD == AUTH_METHOD_ECDSA_P256 )
  {
    hash_sz = 32;
  }
  else
  {
    hash_sz = 48;
  }
  
  if( false == GenerateHash(hash_sz, (uint8_t *)img_address, p_header->FW_IMG_LEN, digest) )
  {
    return false;
  }
  
  rom_memset(sdigest, 0, 64);
  if( false == EncryptHash(digest, hash_sz, sdigest))
  {
    return false;
  }
  
  return true;
}

bool saveEncryptedHash(FW_IMG_HDR *p_header, uint32_t img_address)
{
  uint8_t sdigest[64] __attribute__((__aligned__(64)));
  uint32_t hash_address, flash_erase_address;
  uint8_t buffer[FLASH_PAGE_SIZE];
  int int_status;
  bool status;
//  uint8_t slot_num;
  uint8_t key_size;
  
//  if( img_address > slots512kFlash[1].hdrOffset )
//  {
//    slot_num = 1;
//  }
//  else
//  {
//    slot_num = 0;
//  }
  
  status = getEncryptedHash(p_header, img_address, sdigest);
  if( status == false )
  {
    return false;
  }
          
  // find the end of image
  hash_address = img_address + p_header->FW_IMG_LEN;
  hash_address = (hash_address%16==0) ? hash_address:(hash_address + (16-hash_address%16));
  flash_erase_address = hash_address - (hash_address%FLASH_PAGE_SIZE);
  rom_memcpy(buffer, (uint8_t *)(flash_erase_address), FLASH_PAGE_SIZE);
  
  // check if there is space for hash code
//  if(slot_num == 1) 
//  {
//    if( (hash_address+48) > (slots512kFlash[1].hdrOffset+slots512kFlash[1].slotSize[0]))
//    {
//      return true;
//    }
//  }
//  else
//  {
//    if( (hash_address+48) > slots512kFlash[1].hdrOffset )
//    {
//      FW_IMG_HDR iheader;
//      rom_memcpy((uint8_t *)&iheader, (uint8_t *)slots512kFlash[1].hdrOffset, sizeof(FW_IMG_HDR));
//      status = checkImgHeader(&iheader);
//      if( status ) // if slot 1 already have valid image header
//      {
//        return true;
//      }
//    }
//  }
  
  if( p_header->MD_AUTH_METHOD == (uint8_t)AUTH_METHOD_ECDSA_P256 )
  {
    key_size = 32;
  }
  else
  {
    key_size = 48;
  }
  if( (hash_address%FLASH_PAGE_SIZE)+key_size > FLASH_PAGE_SIZE )
  {
    uint32_t part1_sz;
    part1_sz = FLASH_PAGE_SIZE - (hash_address%FLASH_PAGE_SIZE);
    rom_memcpy(&buffer[hash_address%FLASH_PAGE_SIZE], sdigest, part1_sz);
    int_status = Flash_EraseSector(flash_erase_address, 2);
    if( int_status != 0 )
    {
      return false;
    }
    int_status = Flash_WriteData(buffer, flash_erase_address, FLASH_PAGE_SIZE);
    if( int_status != 0 )
    {
      return false;
    }
    rom_memcpy(&buffer[0], &sdigest[part1_sz], (key_size-part1_sz));
    int_status = Flash_WriteData(buffer, (flash_erase_address+FLASH_PAGE_SIZE), (key_size-part1_sz));
    if( int_status != 0 )
    {
      return false;
    }
  }
  else
  {
    rom_memcpy(&buffer[hash_address%FLASH_PAGE_SIZE], sdigest, key_size);
    int_status = Flash_EraseSector(flash_erase_address, 1);
    if( int_status != 0 )
    {
      return false;
    }
    int_status = Flash_WriteData(buffer, flash_erase_address, FLASH_PAGE_SIZE);
    if( int_status != 0 )
    {
      return false;
    }
  }

  return true;
  
}

bool validEXTHeader(EXT_FLASH_HEADER *extf_header)
{
  uint32_t coherence, tmp_seq;
  uint16_t checksum;
  uint8_t i, *data;
  
//  coherence = Swap32(extf_header->coherence);
//  if (rom_memcmp((uint8_t *)&coherence, MANUFACTURE_ID, 4) != 0)
//  {
//    return false;
//  }
  coherence = extf_header->coherence;
  if( rom_memcmp((uint8_t *)&coherence, (uint8_t *)"MCHP", 4) != 0 )
  {
    return false;
  }
  
  if( extf_header->md_rev != 1 )
  {
    return false;
  }
  if( extf_header->pl_dec_key > 1 )
  {
    return false;
  }
  if( extf_header->seq_num == 0 )
  {
    return false;
  }
  checksum = 0;
  tmp_seq = extf_header->seq_num;
  extf_header->seq_num = 0;
  data = (uint8_t *)extf_header;
  for(i = 0; i < 14; i++)
  {
    checksum += data[i];
  }
  extf_header->seq_num = tmp_seq;
  if( checksum != extf_header->checksum )
  {
    return false;
  }
  return true;
}


bool check_int_flash(void)
{
  EXT_FLASH_HEADER extf_header;
  FW_IMG_HDR img_header;
  bool status;
  uint32_t saddr;
  uint8_t plain[READ_BLOCK_SZ];
  uint8_t secured[READ_BLOCK_SZ];
  uint8_t next_iv[AES_BLOCK_SZ];
  
  rom_memcpy((uint8_t *)&extf_header, (uint8_t *)(slots512kFlash[1].hdrOffset), sizeof(EXT_FLASH_HEADER));
  status = validEXTHeader(&extf_header);
  if((status==false) || (extf_header.seq_num < 0xFFFFFFFF) )
  {
    return false;
  }
  
  saddr = slots512kFlash[1].hdrOffset+sizeof(EXT_FLASH_HEADER);
  if( extf_header.pl_dec_mthd == 0 )
  {
    rom_memcpy((uint8_t *)&img_header, (uint8_t *)saddr, sizeof(FW_IMG_HDR));
  }
  else
  {
    rom_memcpy(secured, (uint8_t *)saddr, READ_BLOCK_SZ);
    rom_memcpy(next_iv, &secured[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
    status = aes_cbc_decrpyt(secured, plain, READ_BLOCK_SZ, (uint8_t *) aes_iv);
    if( status == false )
    {
      return false;
    }
    rom_memcpy((uint8_t *)&img_header, plain, sizeof(FW_IMG_HDR));
  }
  status = checkImgHeader(&img_header);
  if( (status == false ) || (img_header.MD_SEQ_NUM < 0xFFFFFFFF) )
  {
    return false;
  }
  
  print_buf((uint8_t *) "Found Unauthorized Image\r\n", 26);
  Flash_Initialize();
  SILEX_REGS->SILEX_CRYPTOCON = 0x02;
  status = ImageAuthentication(saddr, MANUFACTURE_ID, false, extf_header.pl_dec_mthd);
  if( status == false )
  {
    // erase unauthorized image
    print_buf((uint8_t *)"Image Authentication Failed\r\n", 29);
    Flash_EraseSector(slots512kFlash[1].hdrOffset, 1);
    return false;
  }
  print_buf((uint8_t *)"Authenticated Image\r\n", 21);
  
  status = CopyFlashImage(saddr, extf_header.pl_dec_mthd, extf_header.crc16, false, true);
  return status;
}


bool check_ext_flash(void)
{
  EXT_FLASH_HEADER extf_header;
  bool status;
  uint32_t taddr;
  uint8_t ext_slot_idx;
  
  sst26_hdl = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
  if( DRV_HANDLE_INVALID == sst26_hdl )
  {
    return false;
  }
  
  for(ext_slot_idx = 0; ext_slot_idx < EXT_FLASH_MAX_IMG_NUM; ext_slot_idx++)
  {
    status = DRV_SST26_Read( sst26_hdl, &extf_header, sizeof(EXT_FLASH_HEADER), (EXT_FLASH_START_ADDR+EXT_FLASH_MAX_IMG_SZ*ext_slot_idx));
    if( status == false )
    {
      return false;
    }
    status = validEXTHeader(&extf_header);
    if( status && (extf_header.seq_num == 0xFFFFFFFF) )
    {
      break;
    }
  }

  DRV_SST26_Close(sst26_hdl);
  sst26_hdl = DRV_HANDLE_INVALID;
  if( ext_slot_idx >= EXT_FLASH_MAX_IMG_NUM )
  {
    return false;
  }
  
  print_buf((uint8_t *)"Found Unauthenticated Image in Ext Flash\r\n", 43);
  
  taddr = EXT_FLASH_START_ADDR+EXT_FLASH_MAX_IMG_SZ*ext_slot_idx;
  status = ImageAuthentication((taddr+EXT_FLASH_HDR_SZ), MANUFACTURE_ID, true, extf_header.pl_dec_mthd);
  if (status == false )
  {
    print_buf((uint8_t *)"Image Authentication failed in Ext Flash\r\n", 42); 
    DRV_SST26_SectorErase(sst26_hdl, taddr);
    delay(0x30000);
    DRV_SST26_Close(sst26_hdl);
    sst26_hdl = DRV_HANDLE_INVALID;
    return false;
  }
  
  print_buf((uint8_t *)"Authenticated Image in Ext Flash\r\n", 34); 
  DRV_SST26_Close(sst26_hdl);
  sst26_hdl = DRV_HANDLE_INVALID;
  
  status = CopyFlashImage((taddr+EXT_FLASH_HDR_SZ), extf_header.pl_dec_mthd, extf_header.crc16, true, true);
  return status;
}




bool check_images(void)
{
  uint8_t slot_idx, chosen_slot;
  bool status;
  FW_IMG_HDR iheader;
  uint8_t sdigest[64] __attribute__((__aligned__(64)));
  uint8_t saved_sdigest[64];
  uint32_t hash_address, img_start_address;
  uint8_t cmp_sz;
  
  for(slot_idx = 0; slot_idx < 2; slot_idx++)
  {
    rom_memcpy((uint8_t *)&iheader, (uint8_t *)slots512kFlash[slot_idx].hdrOffset, sizeof(FW_IMG_HDR));
    if( validMetaHeader(&iheader) && (iheader.MD_SEQ_NUM == 0xFFFFFFFF))
    {
      break;
    }
  }
  if( slot_idx < 2 )
  {
    print_buf((uint8_t *)"Found new Executable Image in Internal Flash\r\n", 46);
    img_start_address = slots512kFlash[slot_idx].hdrOffset;
    status = ImageAuthentication(img_start_address, MANUFACTURE_ID, false, false);
    if( status == false )
    {
      Flash_EraseSector(img_start_address, 1);
    }
    else if( (iheader.FW_IMG_SRC_ADDR != iheader.FW_IMG_DST_ADDR) && (slot_idx == 1) )
    {
      print_buf((uint8_t *)"Authenticated Image\r\n", 21);
      status = CopyFlashImage(img_start_address, 0, 0, false, false);
    }
  }
  
  minimum_seq(&chosen_slot);
  if( chosen_slot > 1 )
  {
    print_buf((uint8_t *)"No Valid Image Found\r\n", 22);
    return false;
  }
  
  img_start_address = slots512kFlash[chosen_slot].hdrOffset;
  rom_memcpy((uint8_t *)&iheader, (uint8_t *)img_start_address, sizeof(FW_IMG_HDR));
  status = getEncryptedHash(&iheader, (img_start_address+METADATA_HEADER_SIZE), sdigest);
  
  hash_address = img_start_address + METADATA_HEADER_SIZE + iheader.FW_IMG_LEN;
  hash_address = (hash_address%16==0) ? hash_address:(hash_address + (16-hash_address%16));
  if( iheader.MD_AUTH_METHOD == AUTH_METHOD_ECDSA_P256 )
  {
    cmp_sz = 32;
  }
  else
  {
    cmp_sz = 48;
  }
  rom_memcpy(saved_sdigest, (uint8_t *)hash_address, cmp_sz);
  if( rom_memcmp(saved_sdigest, sdigest, cmp_sz) == 0 )
  {
    print_buf((uint8_t *)"Match hash, Jump to App\r\n", 25);
    ApplicationTransition(img_start_address+METADATA_HEADER_SIZE);
    return true;
  }
  
  status = ImageAuthentication(img_start_address, MANUFACTURE_ID, false, false);
  if( status == false )
  {
    Flash_EraseSector(img_start_address, 1);
    return false;
  }
  
  status = saveEncryptedHash(&iheader, (img_start_address+METADATA_HEADER_SIZE));
  if( status == false )
  {
    return false;
  }
  print_buf((uint8_t *)"Recreated hash, Jump to App\r\n", 29);
  ApplicationTransition(img_start_address+METADATA_HEADER_SIZE);
  return true;
}

void cryptoEngineInit(void)
{
  SILEX_REGS->SILEX_CRYPTOCON = 0x02;

}

// *****************************************************************************
// *****************************************************************************
// Section: Application Initialization and State Machine Functions
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void APP_Initialize ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Initialize ( void )
{
    /* Place the App state machine in its initial state. */
    appData.state = APP_STATE_INIT;

    

    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
}




/******************************************************************************
  Function:
    void APP_Tasks ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Tasks ( void )
{

    /* Check the application's current state. */
    switch ( appData.state )
    {
        /* Application's initial state. */
        case APP_STATE_INIT:
        {
            bool appInitialized = true;


            if (appInitialized)
            {

                appData.state = APP_STATE_SERVICE_TASKS;
            }
            break;
        }

        case APP_STATE_SERVICE_TASKS:
        {
	
			bool status = false;
  			uint32_t portv;
  			uint32_t pval = 1;
	
			<#if (BOOTLOADER_DFU_ENABLE == true) && (BOOTLOADER_DFU_MODE == "GPIO_TRIGGER")>
			/* Set to Digital mode */
  			((gpio_registers_t*)GPIO_${BOOTLOADER_GPIO_PORT})->GPIO_ANSELCLR = (1 << ${BOOTLOADER_GPIO_PIN});
  			/* Read the GPIO Port for Button Press Identification */
  			portv = ((gpio_registers_t*)GPIO_${BOOTLOADER_GPIO_PORT})->GPIO_PORT;
  			pval = portv & (1 << ${BOOTLOADER_GPIO_PIN});
  			/* If button is not pressed, check for the image and jump to application 
     		If pressed, jump to DFU Mode */
			</#if>
  	    	
			if( pval == 0)
  	    	{
              print_buf((uint8_t *)"Start DFU\r\n", 11);
              start_dfu();
            }
            else
            {
              cryptoEngineInit();
              
              status = check_ext_flash();

              status = check_int_flash();
              
              status = check_images();
              if( status == false )
              {
                delay(0x30000);
                if( restore_sercom0_hs )
                {
                  CFG_REGS->CFG_CFGCON1CLR = CFG_CFGCON1_SCOM0_HSEN(1);
                }
              }
              
            }
            
            
            while(1);
            break;
        }

        /* The default state should never be executed. */
        default:
        {
            /* TODO: Handle error in application's state machine. */
            break;
        }
    }
}


/*******************************************************************************
 End of File
 */
