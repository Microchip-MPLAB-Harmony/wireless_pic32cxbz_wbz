#include <stdlib.h>

#include "security.h"
#include "application.h"
//#include "component/rot.h"

extern uint8_t Flash_EraseSector(uint32_t addr, uint16_t pageCount);
extern void delay(uint32_t value);

//volatile unsigned int usrmem[(1024*16+100)/4];
volatile unsigned int *usrmem;
IMAGE_LOADER_CONTEXT_ECDSA iCtxEcdsa; 

const char aes_key[AES_BLOCK_SZ] = {0xAA,0xBB,0xCC,0xDD,0xEE,0xFF,0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99};
const uint8_t aes_iv[AES_BLOCK_SZ]  = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};


DRV_HANDLE sst26_hdl;

const uint8_t KEY_LENGTHS[AUTH_METHOD_MAX] = {
    0, 0, 32, 48
};
    
void rom_memcpy32(uint32_t * dst, uint32_t * src, uint32_t count)
{
    while(count-- > 0)
    {
        *dst++ = *src++;
    }
}
void rom_memcpy(uint8_t * dst, uint8_t * src, uint32_t count)
{
    while(count-- > 0)
    {
        *dst++ = *src++;        
    }
}
uint8_t rom_memcmp(uint8_t * data1, uint8_t * data2, uint32_t count)
{
  uint32_t i;
  
  for(i = 0; i < count; i++)
  {
      if( data1[i] != data2[i] )
      {
        return (data2[i]-data1[i]);
      }
  }
  return 0;
}

void rom_memset(uint8_t * addr, uint8_t value, uint32_t count)
{
    while(count-- > 0)
    {
        *addr++ = value;
    }    
}

void rom_memset32(uint32_t * addr, uint32_t value, uint32_t count)
{
    while(count-- > 0)
    {
        *addr++ = value;
    }
}

bool aes_cbc_decrpyt(uint8_t *input, uint8_t *output, size_t sz, uint8_t *iv)
{
  int status = -1;
  struct sxkeyref key_ref;
  struct sxblkcipher cipher;
  
  // enable crypto
  SILEX_REGS->SILEX_CRYPTOCON = 0x02;
  key_ref = SX_KEYREF_LOAD_MATERIAL(AES_BLOCK_SZ, aes_key);
  status = SX_BLKCIPHER_CREATE_AESCBC_DEC(&cipher, (const struct sxkeyref *)&key_ref, (const char *) iv);
  if( status != SX_OK )
  {
    while(1);
    return false;
  }
  
  status = SX_BLKCIPHER_CRYPT(&cipher, (const char *)input, sz, (char *)output);
  if (status != SX_OK )
  {
    while(1);
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



bool ecdsa_ver_start_flash(uint8_t * hash, size_t hashLen, 
        uint8_t * qx, uint8_t * qy, uint8_t * r, uint8_t * s, uint8_t authMethod)
{
    struct sx_pk_cnx *cnx;
    struct sx_buf h_buf;
    struct sx_buf qx_buf;
    struct sx_buf qy_buf;
    struct sx_buf r_buf;
    struct sx_buf s_buf;
    struct sx_pk_ecurve curve;
    
    iCtxEcdsa.cfg.maxpending = 0;
    iCtxEcdsa.cfg.devidx = 0;
    iCtxEcdsa.cfg.usrmem = (long long*) usrmem;
    iCtxEcdsa.cfg.usrmemsz = 0x4064;
    iCtxEcdsa.cfg.personalization = NULL;
    iCtxEcdsa.cfg.personalization_sz = 0;

    qx_buf.bytes = (char *)qx;
    qy_buf.bytes = (char *)qy;
    r_buf.bytes = (char *)r;
    s_buf.bytes = (char *)s;
    h_buf.bytes = (char *)hash;
   
    // Note: Qx, Qy, R, and S must be zero-padded
    if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P256)
    {
        qx_buf.sz = 32;
        qy_buf.sz = 32;
        r_buf.sz = 32;
        s_buf.sz = 32;
        h_buf.sz = 32;
    }
    else
    {
        qx_buf.sz = 48;
        qy_buf.sz = 48;
        r_buf.sz = 48;
        s_buf.sz = 48;
        h_buf.sz = 48;
    }

    rom_memset32((uint32_t *)usrmem, 0x00, 0x1019);

    cnx = SX_PK_OPEN(&iCtxEcdsa.cfg);
    if (cnx != NULL)
    {
        if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P256)
        {
            curve = SX_PK_GET_CURVE_NISTP256(cnx);
        }
        else
        {
            curve = SX_PK_GET_CURVE_NISTP384(cnx);
        }
        //iCtxEcdsa.pkreq = sx_async_ecdsa_verify_go((const struct sx_pk_ecurve *)&curve, &qx_buf, &qy_buf, &r_buf, &s_buf, &h_buf);
        iCtxEcdsa.pkreq.status = sx_ecdsa_verify((const struct sx_pk_ecurve *)&curve, &qx_buf, &qy_buf, &r_buf, &s_buf, &h_buf);
        if (iCtxEcdsa.pkreq.status)
        {
            return false;
        }
        
        return true;
    }

    return false;
}

int ecdsa_get_status_flash(void)
{
    int status;
   
    status = SX_PK_GET_STATUS(iCtxEcdsa.pkreq.req);

    switch(status)
    {
        case SX_OK:
            SX_PK_RELEASE_REQ(iCtxEcdsa.pkreq.req);
            SX_PK_CLOSE((struct sx_pk_cnx*)usrmem);
            return SX_OK;
        case SX_ERR_BUSY:
            return SX_ERR_BUSY;
        default:
            SX_PK_RELEASE_REQ(iCtxEcdsa.pkreq.req);
            SX_PK_CLOSE((struct sx_pk_cnx*)usrmem);
            return SX_ERR_UNKNOWN_ERROR;
    }
}



void ExtractBootKeyX(uint8_t * parity, uint8_t * x, uint8_t authMethod, uint8_t authKey) {
    uint8_t keyLen = 0;
    uint8_t * i = (uint8_t *) SECURE_BOOT_KEY_ADDRESS;
    
    if (authMethod < AUTH_METHOD_MAX) {
        keyLen = KEY_LENGTHS[authMethod];
        rom_memset(x, 0x00, MAX_AUTH_KEY_LEN);
        while (keyLen-- > 0) {
            *x++ = *i--;
        }
        *parity = (uint8_t) ((SECCFG & 0x00010000) >> 16);
    } else {
        // This should be caught by the header validation function so if it 
        // occurs here it's a critical failure
        while(1);
    }
}



bool ecdsa_yrecover(uint8_t * y, uint8_t * x, const int parity, uint8_t authMethod)
{
    int status;
    struct sx_pk_cnx *cnx;
    //struct sx_pk_cnx context;
    
    struct sx_pk_config cfg = 
    {
        .maxpending = 0,
        .devidx = 0,
        .usrmem = (long long *) usrmem,
        .usrmemsz = 0x4064,       
        .personalization = NULL,
        .personalization_sz = 0
    };    
    struct sx_buf x_buf;
    sx_op y_buf;
    struct sx_pk_ecurve curve;
    
    rom_memset((uint8_t *) usrmem, 0x00, 0x4064);
    
    
    x_buf.bytes = (char *)x;
    rom_memset(y, 0x00, 48);
    y_buf.bytes = (char *)y;
    
    if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P256)
    {
        y_buf.sz = 32;
        x_buf.sz = 32;
    }
    else //p384
    {
        y_buf.sz = 48;
        x_buf.sz = 48;
    }

    cnx = SX_PK_OPEN(&cfg);

    if (cnx != NULL)
    {
        if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P384)
        {
            curve = SX_PK_GET_CURVE_NISTP384(cnx);
        }
        else
        {
            curve = SX_PK_GET_CURVE_NISTP256(cnx);
        }
        status = sx_ec_pt_decompression((const struct sx_pk_ecurve *)&curve, &x_buf, parity, &y_buf);

        SX_PK_CLOSE(cnx);

        if (status == SX_OK)
        {
            return true;
        }
    }

    return false;

}


bool IMG_MEM_AuthenticateHeaderStart_flash(uint8_t * digest, FW_IMG_HDR * hdr, uint8_t * x, uint8_t * y)
{
    uint32_t tempSrcAddr = hdr->FW_IMG_SRC_ADDR;
    uint32_t authMethod = hdr->MD_AUTH_METHOD;
    int r;
    struct sxhash ctx;
    
    //authflowcheck += METHOD_STEP_3;     
    // Note: replacing this source address could cause an SRAM-based header to 
    // become corrupted if a reset occurs before it can be restored.  However, 
    // no processes should use the source address after the image header has 
    // been copied to SRAM, so this shouldn't cause an issue
    hdr->FW_IMG_SRC_ADDR = 0;
    
    rom_memset (digest, 0x00, 64);
    
    rom_memset((uint8_t *)&ctx, 0x00, sizeof(struct sxhash));
    if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P256)
    {
        r = SX_HASH_CREATE_SHA256(&ctx, sizeof(struct sxhash));
    }
    else //p384
    {
        r = SX_HASH_CREATE_SHA384(&ctx, sizeof(struct sxhash));
    }

    if (r != SX_OK)
    {
        return false;
    }
    
    // Feed in header data
    r = SX_HASH_FEED(&ctx, (const char *)&hdr->FW_IMG_REV, FW_IMAGE_HEADER_HASH_SIZE);
    
    if (r != SX_OK)
    {
        return false;
    }
    
    r = SX_HASH_DIGEST(&ctx, (char *) digest);

    if (r != SX_OK)
    {
        return false;
    }

    do
    {
        r = SX_HASH_STATUS(&ctx);
    } while (r == SX_ERR_HW_PROCESSING);

    if (r != SX_OK)
    {
        return false;
    }
    if(authMethod == (uint8_t) AUTH_METHOD_ECDSA_P256)
    {
      if (ecdsa_ver_start_flash(digest, 32, x, y, hdr->MD_SIG, hdr->MD_SIG + 32, hdr->MD_AUTH_METHOD) == false)
        {
            return false;
        }  
    }
    
    else //p384
    {
        if (ecdsa_ver_start_flash(digest, 48, x, y, hdr->MD_SIG, hdr->MD_SIG + 48, hdr->MD_AUTH_METHOD) == false)
        {
            return false;
        }
    }
    hdr->FW_IMG_SRC_ADDR = tempSrcAddr;
    return true;
}

void NullCheck(uint8_t * key, uint8_t * keyInv, uint8_t authMethod, uint8_t authKey) {
    uint8_t keyLen = KEY_LENGTHS[authMethod];
    uint8_t * keyPtr = (uint8_t *) SECURE_BOOT_KEY_ADDRESS;
    
    //allows plain authentication only when keyLen = 0 and image header matches the case
   if ((keyLen == 0) && (authMethod == AUTH_METHOD_NONE))
    {
       *key = 0;
       *keyInv = 0xFF;
        return;
    }
    //if CRC mode
   else if(keyLen == 0)
   {
       return;
   }
    
    //ECDSA p256 and ECDSA p384; keyLen!= 0
    *key = *keyPtr;
    *keyInv = ~(*keyPtr--);
    keyLen--;
    while (keyLen-- != 0)
    {
        *key |= *keyPtr;
        *keyInv &= ~(*keyPtr);
        keyPtr--;
    }
}

static void NullCheckWrap(uint8_t * ret, uint8_t value, uint8_t authMethod, uint8_t authKey)
{
    uint8_t nullkey = 0, nullkeyInv = 0;

    NullCheck(&nullkey, &nullkeyInv, authMethod, authKey);
    if ((uint8_t)(~nullkey) != nullkeyInv)
    {
        while(1);
    }
    if ((nullkey == 0) && (nullkeyInv == 0xFF))
    {
        *ret |= value;
    }    
}

uint32_t SecurityStatusGet(void)
{
    uint32_t retVal = 0;
    uint32_t secBoot = 0;
    uint32_t codeProt = 0;
    
    //Read dbg lck status to determine whether the device is secured or not
    secBoot = ((SECCFG & ROT_SECCFG_DEBUG_LCK_Msk) >> ROT_SECCFG_DEBUG_LCK_Pos) ;
            
    //Read code protection status
    codeProt = (((DSU_REGS->DSU_STATUSB) & DSU_STATUSB_PROT_Msk) >> DSU_STATUSB_PROT_Pos);
    
    if ((secBoot == 0b01) || (secBoot == 0b10) || (secBoot == 0b11))
    {
        // Secured
        if (codeProt == 0b01)
        {
            // Code Protected
            retVal = MAGIC_NUMBER_SECURED_CODE_PROTECT;
        }
        else if (codeProt == 0b00)
        {
            // Not code protected
            retVal = MAGIC_NUMBER_SECURED;
        }
    }
    else if (secBoot == 0b00)
    {
        // Not Secured
        if (codeProt == 0b01)
        {
            // Code Protected
            retVal = MAGIC_NUMBER_CODE_PROTECT;
        }
        else if (codeProt == 0b00)
        {
            // Not code protected
            retVal = MAGIC_NUMBER_NO_PROTECT;
        }        
    }
    else
    {
        //control should come this logic
        while(1);
    }

    //return secStatus, used all through the program
    return retVal;
}

bool LoadandAuthenticate(uint32_t image_start_addr, FW_IMG_HDR *pHdr, bool is_ext_flash, bool is_encrypted, uint8_t *iv)
{
  uint8_t parityXHdr = 0;
  uint8_t xHdr[MAX_AUTH_KEY_LEN];
  uint8_t yHdr[MAX_AUTH_KEY_LEN];
  uint8_t * xImg = xHdr;
  uint8_t * yImg = yHdr;
  uint8_t digest[64] __attribute__((__aligned__(64)));
  struct sxhash imgHashCtx;
  int r;
  uint8_t authHdr = 0;
  uint32_t secStatus = SecurityStatusGet();
  uint8_t encrypt_buffer[READ_BLOCK_SZ];
  uint8_t buffer[READ_BLOCK_SZ];
  uint8_t next_iv[AES_BLOCK_SZ];
  uint16_t i, blocks;
  uint16_t block_sz;
  bool status;
  
  if ((pHdr->MD_AUTH_METHOD != pHdr->FW_IMG_AUTH_METHOD) || (pHdr->MD_AUTH_KEY != pHdr->FW_IMG_AUTH_KEY))
  {
      return false;
  }
  
  if( pHdr->MD_AUTH_METHOD == AUTH_METHOD_NONE )
  {
    return true;
  }
  
  if( is_encrypted )
  {
    rom_memcpy(next_iv, iv, AES_BLOCK_SZ);
  }
  
  authHdr = 0;
  xHdr[20] = 0xFF;
  xHdr[0] = 0x55;
  xHdr[47] = 0xAA;
  ExtractBootKeyX(&parityXHdr, xHdr, pHdr->MD_AUTH_METHOD, pHdr->MD_AUTH_KEY);      

  // Check this two times to minimize the chances that a fault could allow an 
  // attacker to bypass authentication
  //NullCheckWrap, when twice called returns MAGIC_NUMBER_AUTH_HDR_AB when metadata/image authentication is not set.
  NullCheckWrap(&authHdr, MAGIC_NUMBER_AUTH_HDR_A, pHdr->MD_AUTH_METHOD, pHdr->MD_AUTH_KEY);
  NullCheckWrap(&authHdr, MAGIC_NUMBER_AUTH_HDR_B, pHdr->MD_AUTH_METHOD, pHdr->MD_AUTH_KEY);

  if ((secStatus != MAGIC_NUMBER_SECURED) && 
      (secStatus != MAGIC_NUMBER_SECURED_CODE_PROTECT) && 
      (authHdr == MAGIC_NUMBER_AUTH_HDR_AB))
  {
    return true;
  }
  
  if(ecdsa_yrecover(yHdr, xHdr, parityXHdr, pHdr->MD_AUTH_METHOD) == false)
  {
      return false;
  }

  if (IMG_MEM_AuthenticateHeaderStart_flash(digest, pHdr, xHdr, yHdr) == false)
  {
      return false;
  }

  
  rom_memset (digest, 0x00, 64);    
  rom_memset ((uint8_t *)&imgHashCtx, 0x00, sizeof(struct sxhash));    
  if(pHdr->MD_AUTH_METHOD == (uint8_t) AUTH_METHOD_ECDSA_P256)
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
  
  if( is_ext_flash )
  {
    
    blocks = pHdr->FW_IMG_LEN/READ_BLOCK_SZ;
    if( pHdr->FW_IMG_LEN%READ_BLOCK_SZ > 0 )
    {
      blocks++;
    }
    for(i = 0; i < blocks; i++)
    {
      if( i == (blocks-1) && (pHdr->FW_IMG_LEN%READ_BLOCK_SZ > 0))
      {
        block_sz = pHdr->FW_IMG_LEN%READ_BLOCK_SZ;
      }
      else
      {
        block_sz = READ_BLOCK_SZ;
      }
      
      if( is_encrypted )
      {
        status = DRV_SST26_Read( sst26_hdl, encrypt_buffer, block_sz, image_start_addr+HEADER_SIZE+i*READ_BLOCK_SZ);
        status = aes_cbc_decrpyt(encrypt_buffer, buffer, block_sz, next_iv);
        if( status == false )
        {
          return false;
        }
        rom_memcpy(next_iv, &encrypt_buffer[block_sz-AES_BLOCK_SZ], AES_BLOCK_SZ);
      }
      else
      {
        status = DRV_SST26_Read( sst26_hdl, buffer, block_sz, image_start_addr+HEADER_SIZE+i*READ_BLOCK_SZ);
        if( status == false )
        {
          return false;
        }
      }
      r = SX_HASH_FEED(&imgHashCtx, (const char *)buffer, block_sz);
      if (r != SX_OK)
      {
          return false;
      }
      
      if( i < (blocks-1) )
      {
        r = SX_HASH_SAVE_STATE(&imgHashCtx);
        if (r != SX_OK)
        {
            return false;
        }
        r = SX_HASH_WAIT(&imgHashCtx);
        if (r != SX_OK)
        {
            return false;
        }
        
        r = SX_HASH_RESUME_STATE(&imgHashCtx);
        if (r != SX_OK)
        {
            return false;
        }
      }
    }
  }
  else
  {
    if( is_encrypted )
    {
      blocks = pHdr->FW_IMG_LEN/READ_BLOCK_SZ;
      if( pHdr->FW_IMG_LEN%READ_BLOCK_SZ > 0 )
      {
        blocks++;
      }
      for(i = 0; i < blocks; i++)
      {
        if( i == (blocks-1) && (pHdr->FW_IMG_LEN%READ_BLOCK_SZ > 0))
        {
          block_sz = pHdr->FW_IMG_LEN%READ_BLOCK_SZ;
        }
        else
        {
          block_sz = READ_BLOCK_SZ;
        }

        rom_memcpy(encrypt_buffer, (uint8_t *)(image_start_addr+HEADER_SIZE+i*READ_BLOCK_SZ), block_sz);
        status = aes_cbc_decrpyt(encrypt_buffer, buffer, block_sz, next_iv);
        if( status == false )
        {
          return false;
        }
        rom_memcpy(next_iv, &encrypt_buffer[block_sz-AES_BLOCK_SZ], AES_BLOCK_SZ);

        r = SX_HASH_FEED(&imgHashCtx, (const char *)buffer, block_sz);
        if (r != SX_OK)
        {
            return false;
        }

        if( i < (blocks-1) )
        {
          r = SX_HASH_SAVE_STATE(&imgHashCtx);
          if (r != SX_OK)
          {
              return false;
          }
          r = SX_HASH_WAIT(&imgHashCtx);
          if (r != SX_OK)
          {
              return false;
          }

          r = SX_HASH_RESUME_STATE(&imgHashCtx);
          if (r != SX_OK)
          {
              return false;
          }
        }
      }
    }
    else
    {
      r = SX_HASH_FEED(&imgHashCtx, (const char *)(image_start_addr+HEADER_SIZE), pHdr->FW_IMG_LEN);
      if (r != SX_OK)
      {
          return false;
      }
    }
  }
  
  r = SX_HASH_DIGEST(&imgHashCtx, (char *) digest);
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
 
  if(pHdr->FW_IMG_AUTH_METHOD == (uint8_t) AUTH_METHOD_ECDSA_P256)
  {
       if (ecdsa_ver_start_flash(digest, 32, xImg, yImg, pHdr->FW_IMG_SIG, pHdr->FW_IMG_SIG + 32, pHdr->FW_IMG_AUTH_METHOD) == false)
      {
          return false;
      }
  }
  else
  {
      if (ecdsa_ver_start_flash(digest, 48, xImg, yImg, pHdr->FW_IMG_SIG, pHdr->FW_IMG_SIG + 48, pHdr->FW_IMG_AUTH_METHOD) == false)
      {
          return false;
      }
  }
  do
  {
      r = ecdsa_get_status_flash();
      switch(r)
      {
          case SX_OK:
              break;
          default:
              return false;
      }
  } while (r == 3);

  
  return true;
}

bool FindItem(const uint8_t * list, uint8_t listSize, uint8_t value)
{
    uint32_t i = 0;
    
    for (i = 0; i < listSize; i++)
    {
        if (*list++ == value)
        {
            return true;
        }
    }
    
    return false;
}


uint16_t crc16(uint8_t* data_p, size_t length, uint16_t init)
{
    unsigned char x;
    unsigned short crc = init;

    while (length--){
        x = crc >> 8 ^ *data_p++;
        x ^= x>>4;
        crc = (crc << 8) ^ ((unsigned short)(x << 12)) ^ ((unsigned short)(x <<5)) ^ ((unsigned short)x);
    }
    return crc;
}


bool validMetaHeader(FW_IMG_HDR *fwHdr)
{
  uint8_t rbctrInv;
  
  if (fwHdr->MD_REV != 0x01)
  {
      return false;
  }
  
  if (fwHdr->MD_SEQ_NUM == 0x00000000)
  {
      return false;
  }

  if (((uint8_t)(RBCTR & 0xFF)) > ((fwHdr->FW_IMG_REV >> 24) & 0xFF))
  {
      return false;
  }

  rbctrInv = ~(RBCTR & 0xFF);
  if (rbctrInv < ((fwHdr->FW_IMG_REV >> 24) & 0xFF))
  {
      return false;
  }
  
    // Validate authentication/decryption key indices and methods
  if (FindItem(validKeyTypes.mdAuthKeyMethods, validKeyTypes.mdAuthKeyMethodCount, fwHdr->MD_AUTH_METHOD) == false)
  {
      return false;
  }    
  if (FindItem(validKeyTypes.mdAuthKeyIndicies, validKeyTypes.mdAuthKeyIndexCount, fwHdr->MD_AUTH_KEY) == false)
  {
      return false;
  }
  if (FindItem(validKeyTypes.mdDecKeyMethods, validKeyTypes.mdDecKeyMethodCount, fwHdr->MD_DEC_METHOD) == false)
  {
      return false;
  }
  if (FindItem(validKeyTypes.mdDecKeyIndicies, validKeyTypes.mdDecKeyIndexCount, fwHdr->MD_DEC_KEY) == false)
  {
      return false;
  }

  // Validate firmware header keys too
  if (FindItem(validKeyTypes.fwAuthKeyMethods, validKeyTypes.fwAuthKeyMethodCount, fwHdr->FW_IMG_AUTH_METHOD) == false)
  {
      return false;
  }    
  if (FindItem(validKeyTypes.fwAuthKeyIndicies, validKeyTypes.fwAuthKeyIndexCount, fwHdr->FW_IMG_AUTH_KEY) == false)
  {
      return false;
  }
  if (FindItem(validKeyTypes.fwDecKeyMethods, validKeyTypes.fwDecKeyMethodCount, fwHdr->FW_IMG_DEC_METHOD) == false)
  {
      return false;
  }
  if (FindItem(validKeyTypes.fwDecKeyIndicies, validKeyTypes.fwDecKeyIndexCount, fwHdr->FW_IMG_DEC_KEY) == false)
  {
      return false;
  }
  
  
  if (fwHdr->MD_PL_LEN != FW_IMAGE_EXPECTED_PL_LEN)
  {
      return false;
  }

  if (fwHdr->MD_CONT_IDX != FW_IMAGE_EXPECTED_CONT_IDX)
  {
      return false;
  }
  return true;
}




bool ImageAuthentication(uint32_t saddr, char *manu_ID, bool is_ext_flash, bool is_encrypted)
{
  uint32_t offset;
  uint32_t coherence = 0;
  FW_IMG_HDR fwHdr;
  bool status;
  uint8_t encrypt_buffer[READ_BLOCK_SZ];
  uint8_t buffer[READ_BLOCK_SZ];
  uint8_t next_iv[AES_BLOCK_SZ];
  
  offset = saddr + FW_IMG_HDR_OFFSET_MD_COHERENCE;
  if( is_ext_flash )
  {
    sst26_hdl = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
    if( DRV_HANDLE_INVALID == sst26_hdl )
    {
      return false;
    }
    if( is_encrypted )
    {
      status = DRV_SST26_Read( sst26_hdl, encrypt_buffer, 16, saddr);
      if( status == false )
      {
        return false;
      }
      status = aes_cbc_decrpyt(encrypt_buffer, buffer, 16, (uint8_t *) aes_iv);
      if( status == false )
      {
        return false;
      }
      rom_memcpy((uint8_t *)&coherence, &buffer[FW_IMG_HDR_OFFSET_MD_COHERENCE], 4);
    }
    else
    {
      status = DRV_SST26_Read( sst26_hdl, &coherence, 4, offset);
    }
  }
  else
  {
    if( is_encrypted )
    {
      rom_memcpy(encrypt_buffer, (uint8_t *)saddr, 16);
      status = aes_cbc_decrpyt(encrypt_buffer, buffer, 16, (uint8_t *)aes_iv);
      if( status == false )
      {
        return false;
      }
      rom_memcpy((uint8_t *)&coherence, &buffer[FW_IMG_HDR_OFFSET_MD_COHERENCE], 4);
    }
    else
    {
      rom_memcpy32(&coherence, (uint32_t *)offset, 1);
    }
  }
  coherence = Swap32(coherence);
  //if (coherence != FW_IMG_HDR_VALUE_MD_COHERENCE)
  if (rom_memcmp((uint8_t *)&coherence, (uint8_t *)manu_ID, 4) != 0)
  {
    return false;
  }
  
  if( is_ext_flash )
  {
    if( is_encrypted )
    {
      status = DRV_SST26_Read( sst26_hdl, encrypt_buffer, READ_BLOCK_SZ, saddr);
      rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
      status = aes_cbc_decrpyt(encrypt_buffer, buffer, READ_BLOCK_SZ, (uint8_t *)aes_iv);
      if( status == false )
      {
        return false;
      }
      rom_memcpy((uint8_t *)&fwHdr, buffer, sizeof(FW_IMG_HDR));
    }
    else
    {
      status = DRV_SST26_Read( sst26_hdl, &fwHdr, sizeof(FW_IMG_HDR), saddr);
    }
  }
  else
  {
    if( is_encrypted )
    {
      rom_memcpy(encrypt_buffer, (uint8_t *)saddr, READ_BLOCK_SZ);
      rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
      status = aes_cbc_decrpyt(encrypt_buffer, buffer, READ_BLOCK_SZ, (uint8_t *)aes_iv);
      if( status == false )
      {
        return false;
      }
      rom_memcpy((uint8_t *)&fwHdr, buffer, sizeof(FW_IMG_HDR));
    }
    else
    {
      rom_memcpy((uint8_t *)&fwHdr, (uint8_t *)saddr, sizeof(FW_IMG_HDR));
    }
  }

  status = validMetaHeader(&fwHdr);
  if( status == false )
  {
    return false;
  }
  
  usrmem = (volatile unsigned int *)malloc(1024*16+100);
  if( usrmem == NULL )
  {
    while(1);
  }
  
  status = LoadandAuthenticate(saddr, &fwHdr, is_ext_flash, is_encrypted, next_iv);
  if( status == false )
  {
    if( is_ext_flash )
    {
      DRV_SST26_SectorErase(sst26_hdl, (saddr&0xFFFFF000));
      delay(0x30000);
      DRV_SST26_Close(sst26_hdl);
      sst26_hdl = DRV_HANDLE_INVALID;
    }
    else
    {
      Flash_EraseSector((saddr&0xFFFFF000), 1);
    }
  }
  free((void *)usrmem);
  
  return status;
}



// Uncomment below sections if CRC Check of external flash/encrypted FW is needed.
uint16_t get_crc16(uint32_t saddr, bool is_ext_flash, bool is_encrypted)
{
  //bool status;
  FW_IMG_HDR *p_header;
  uint8_t buffer[READ_BLOCK_SZ];
  //uint8_t encrypt_buffer[READ_BLOCK_SZ];
  uint16_t cal_crc16;
  uint32_t img_len;
  //uint8_t next_iv[AES_BLOCK_SZ];
  
//  if( is_ext_flash )
//  {
//    sst26_hdl = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
//    if( DRV_HANDLE_INVALID == sst26_hdl )
//    {
//      return 0;
//    }
//    
//    if( is_encrypted == true )
//    {
//      status = DRV_SST26_Read(sst26_hdl, encrypt_buffer, READ_BLOCK_SZ, saddr);
//      if( status == false )
//      {
//        return 0;
//      }
//      rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
//      status = aes_cbc_decrpyt(encrypt_buffer, buffer, READ_BLOCK_SZ, aes_iv);
//      if( status == false )
//      {
//        return 0;
//      }
//    }
//    else
//    {
//      status = DRV_SST26_Read(sst26_hdl, buffer, READ_BLOCK_SZ, saddr);
//      if( status == false )
//      {
//        return 0;
//      }
//    }
//  }
//  else
  {
//    if( is_encrypted == true )
//    {
//      rom_memcpy(encrypt_buffer, (uint8_t *)saddr, READ_BLOCK_SZ);
//      rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
//      status = aes_cbc_decrpyt(encrypt_buffer, buffer, READ_BLOCK_SZ, aes_iv);
//      if( status == false )
//      {
//        return 0;
//      }
//    }
//    else
    {
      rom_memcpy(buffer, (uint8_t *)saddr, READ_BLOCK_SZ);
    }
  }
  
  p_header = (FW_IMG_HDR *)buffer;
  img_len = p_header->FW_IMG_LEN;
  p_header->FW_IMG_SRC_ADDR = 0;
  
  cal_crc16 = crc16(&buffer[16], (READ_BLOCK_SZ-16), 0xffff);
  
//  if( is_ext_flash )
//  {
//    uint16_t block, block_sz, i;
//    
//    if( img_len%READ_BLOCK_SZ > 0 )
//    {
//      block = img_len/READ_BLOCK_SZ+1;
//    }
//    else
//    {
//      block = img_len/READ_BLOCK_SZ;
//    }
//    for(i = 0; i < block; i++)
//    {
//      if( (i < block-1) || (img_len%READ_BLOCK_SZ==0) )
//      {
//        block_sz = READ_BLOCK_SZ;
//      }
//      else
//      {
//        block_sz = img_len%READ_BLOCK_SZ;
//      }
//      
//      if( is_encrypted > 0 )
//      {
//        status = DRV_SST26_Read(sst26_hdl, encrypt_buffer, block_sz, saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ);
//        if( status == false )
//        {
//          return 0;
//        }
//        status = aes_cbc_decrpyt(encrypt_buffer, buffer, block_sz, next_iv);
//        if( status == false )
//        {
//          return 0;
//        }
//        rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
//      }
//      else
//      {
//        status = DRV_SST26_Read(sst26_hdl, buffer, block_sz, saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ);
//        if( status == false )
//        {
//          return 0;
//        }
//      }
//      cal_crc16 = crc16(buffer, block_sz, cal_crc16);
//    }
//    DRV_SST26_Close(sst26_hdl);
//    sst26_hdl = DRV_HANDLE_INVALID;
//  }
//  else
  {
//    if( is_encrypted > 0 )
//    {
//      uint16_t block, block_sz, i;
//
//      if( img_len%READ_BLOCK_SZ > 0 )
//      {
//        block = img_len/READ_BLOCK_SZ+1;
//      }
//      else
//      {
//        block = img_len/READ_BLOCK_SZ;
//      }
//      for(i = 0; i < block; i++)
//      {
//        if( (i < block-1) || (img_len%READ_BLOCK_SZ==0) )
//        {
//          block_sz = READ_BLOCK_SZ;
//        }
//        else
//        {
//          block_sz = img_len%READ_BLOCK_SZ;
//        }
//        rom_memcpy(encrypt_buffer, (uint8_t *)(saddr+READ_BLOCK_SZ+i*READ_BLOCK_SZ), block_sz);
//        status = aes_cbc_decrpyt(encrypt_buffer, buffer, block_sz, next_iv);
//        if( status == false )
//        {
//          return 0;
//        }
//        rom_memcpy(next_iv, &encrypt_buffer[READ_BLOCK_SZ-AES_BLOCK_SZ], AES_BLOCK_SZ);
//        cal_crc16 = crc16(buffer, block_sz, cal_crc16);
//      }
//    }
//    else
    {
      cal_crc16 = crc16((uint8_t *)(saddr+READ_BLOCK_SZ), img_len, cal_crc16);
    }
  }
  
  return cal_crc16;
}


bool crc16_check(uint32_t saddr, bool is_ext_flash)
{
  EXT_FLASH_HEADER extf_header;
  bool status;
  uint16_t cal_crc16;
  
  if( is_ext_flash )
  {
    sst26_hdl = DRV_SST26_Open(sysObj.drvSST26, DRV_IO_INTENT_READWRITE);
    if( DRV_HANDLE_INVALID == sst26_hdl )
    {
      return false;
    }
    status = DRV_SST26_Read( sst26_hdl, &extf_header, EXT_FLASH_HEADER_SZ, saddr);
    if( status == false )
    {
      return false;
    }
    DRV_SST26_Close(sst26_hdl);
    sst26_hdl = DRV_HANDLE_INVALID;
  }
  else
  {
    rom_memcpy((uint8_t *)&extf_header, (uint8_t *)saddr, EXT_FLASH_HEADER_SZ);
  }
  
  if( extf_header.md_rev > 1 )
  {
    return false;
  }
  
  cal_crc16 = get_crc16(saddr+EXT_FLASH_HEADER_SZ, is_ext_flash, extf_header.pl_dec_mthd);
  if( cal_crc16 == extf_header.crc16 )
  {
    return true;
  }
  return false;
}
