#include "driver/security/api_table.h"
#include "driver/security/silexpk/core_api.h"
#include "driver/security/silexpk/internal.h"
#include "driver/security/sxsymcrypt/keyref_api.h"
#include "driver/security/sxsymcrypt/blkcipher_api.h"
#include "driver/security/sxsymcrypt/statuscodes.h"
#include "driver/security/silexpk/sxbufop.h"
#include "driver/security/silexpk/ec_curves_api.h"
#include "driver/security/silexpk/eccweierstrass_api.h"
#include "driver/security/sxsymcrypt/sha2_api.h"
#include "driver/security/sxsymcrypt/hash_api.h"
#include "driver/security/silexpk/statuscodes_api.h"

#include "driver/driver.h"
#include "driver/sst26/drv_sst26.h"

#include "regdef.h"
#include "mem_interface.h"
#include "definitions.h"
#include "application.h"

#define SECURE_BOOT_KEY_ADDRESS             (0x44002C55)
#define FW_IMG_HDR_OFFSET_MD_COHERENCE      6
#define MAX_AUTH_KEY_LEN                    48
#define FW_IMAGE_HEADER_HASH_SIZE           116 //0x84 - 0x10 (meta footer address -  0x10 metadata header length) 
#define FW_IMAGE_EXPECTED_PL_LEN            0x74 // for A0 0xE0 for A1
#define FW_IMAGE_EXPECTED_CONT_IDX          1

// Security status
//fault mitigation - CONSTANT CODING used for flags
#define MAGIC_NUMBER_NO_PROTECT                     ((uint32_t)0x8ebc29bf)
#define MAGIC_NUMBER_CODE_PROTECT                   ((uint32_t)0x5aa5684a)
#define MAGIC_NUMBER_SECURED                        ((uint32_t)0xecd3a0a1)
#define MAGIC_NUMBER_SECURED_CODE_PROTECT           ((uint32_t)0x3b79a901)

#define MAGIC_NUMBER_AUTH_HDR_A     (0x15)
#define MAGIC_NUMBER_AUTH_HDR_B     (0xA3)
#define MAGIC_NUMBER_AUTH_HDR_C     (0x5C)
#define MAGIC_NUMBER_AUTH_HDR_AB    (0xB7)

#define BLKCIPHER_FIRST_ROUND       0x01
#define BLKCIPHER_INTER_ROUND       0x02
#define BLKCIPHER_LAST_ROUND        0x04

#define AES_BLOCK_SZ                16

typedef enum
{
    AUTH_METHOD_NONE = 0,
    AUTH_METHOD_CRC16 = 1,
    AUTH_METHOD_ECDSA_P256 = 2,
    AUTH_METHOD_ECDSA_P384 = 3,
    AUTH_METHOD_MAX = 4
} AUTH_METHODS;


extern const KEYS_SUPPORTED validKeyTypes;
extern const uint8_t aes_iv[];

void rom_memcpy32(uint32_t * dst, uint32_t * src, uint32_t count);
void rom_memcpy(uint8_t * dst, uint8_t * src, uint32_t count);
uint8_t rom_memcmp(uint8_t * data1, uint8_t * data2, uint32_t count);
void rom_memset(uint8_t * addr, uint8_t value, uint32_t count);
void rom_memset32(uint32_t * addr, uint32_t value, uint32_t count);

bool aes_cbc_decrpyt(uint8_t *input, uint8_t *output, size_t sz, uint8_t *iv);
bool ImageAuthentication(uint32_t saddr, char *manu_ID, bool is_ext_flash, bool is_encrypted);
uint16_t get_crc16(uint32_t saddr, bool is_ext_flash, bool is_encrypted);
bool crc16_check(uint32_t saddr, bool is_ext_flash);
bool validMetaHeader(FW_IMG_HDR *fwHdr);
