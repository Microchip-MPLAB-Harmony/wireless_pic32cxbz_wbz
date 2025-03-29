
#include <stdint.h>
#include <stdbool.h>
#include "application.h"

#ifndef _MEM_INTERFACE_H
#define _MEM_INTERFACE_H

// Maximum memory topologies on the device (one SRAM and one Flash))
#define MAX_MEM_TOPOLOGIES                  2
// The maximum possible number of slots (one SRAM slot and 2 Flash slots))
#define MAX_SLOTS                           3
// The size of the reserved header block
#define HEADER_SIZE                         512

typedef enum 
{
    AUTH_STATUS_BUSY = 0x530839fa,
    AUTH_STATUS_FAILED = 0xe97d40ce,
    AUTH_STATUS_SUCCESS = 0x0ac60ce4
} AUTH_STATUS;

typedef struct
{
    uint32_t        hdrOffset;
    uint32_t        slotSize[2];
    bool            executable;
}SLOT_PARAMS;

typedef void (*IMG_MEM_INITIALIZE)(void);
typedef uint8_t (*IMG_MEM_WRITE)(uint8_t * data, uint32_t addr, uint32_t bytes);
typedef uint8_t (*IMG_MEM_READ)(bool fastRead, uint8_t * buffer, uint32_t addr, uint32_t bytes);
typedef uint8_t (*IMG_MEM_ERASE)(uint32_t addr, uint16_t pageCount);
typedef uint32_t (*IMG_MEM_READ_JEDEC_ID)(void);

typedef struct
{
    IMG_MEM_INITIALIZE          fInit;
    IMG_MEM_WRITE               fWrite;
    IMG_MEM_READ                fRead;
    IMG_MEM_ERASE               fErase;
    IMG_MEM_READ_JEDEC_ID       fReadId;
} IMG_MEM_INTERFACE;

typedef struct
{
    uint16_t                    u16ErasePageSz;     // Erase page size
    uint16_t                    u16ProgRowSz;       // Programming row size
    uint32_t                    u32UmmAddrStart;    // Unified memory model address start
    uint32_t                    u32TotSize;         // Total flash size
    uint8_t                     u8SlotCount;        // Count of slots in memory
    const SLOT_PARAMS *         pSlots;             // Pointer to array of slot structs
    uint32_t                    u32CalIdx;          // Index of calibration data
    const IMG_MEM_INTERFACE *   ifFlash;            // Flash interface
    uint8_t                     u8DevIdCount;       // Count of valid device IDs
    const uint32_t *            pDevIds;            // Pointer to array of device IDs
    uint32_t                    u32DevIdMask;       // Device ID negative mask
    uint32_t                    u32AddrPosMask;     // UMM address positive mask
    uint32_t                    u32AddrNegMask;     // UMM addr negative mask
    uint32_t                    u32BlankCheck;     // UMM addr negative mask    
}IMG_MEM_TOPOLOGY;


typedef struct
{
    uint8_t             mdAuthKeyMethodCount;
    const uint8_t *     mdAuthKeyMethods;
    uint8_t             mdAuthKeyIndexCount;    
    const uint8_t *     mdAuthKeyIndicies;

    uint8_t             mdDecKeyMethodCount;
    const uint8_t *     mdDecKeyMethods;
    uint8_t             mdDecKeyIndexCount;    
    const uint8_t *     mdDecKeyIndicies;

    uint8_t             fwAuthKeyMethodCount;
    const uint8_t *     fwAuthKeyMethods;
    uint8_t             fwAuthKeyIndexCount;    
    const uint8_t *     fwAuthKeyIndicies;

    uint8_t             fwDecKeyMethodCount;
    const uint8_t *     fwDecKeyMethods;
    uint8_t             fwDecKeyIndexCount;    
    const uint8_t *     fwDecKeyIndicies;
} KEYS_SUPPORTED;


typedef struct
{
  uint32_t  coherence;
  uint8_t   md_rev;
  uint8_t   pl_dec_mthd;
  uint8_t   pl_dec_key;
  uint8_t   reserved;
  uint32_t  seq_num;
  uint16_t  crc16;
  uint16_t  checksum;
} EXT_FLASH_HEADER;

typedef struct
{
    FW_IMG_HDR *                pHdr;
    const SLOT_PARAMS *         pSlot;
    const IMG_MEM_TOPOLOGY *    pTop;
} VALID_SLOT;

typedef struct
{
    const IMG_MEM_TOPOLOGY *     validTops[MAX_MEM_TOPOLOGIES];
    VALID_SLOT                   validSlots[MAX_SLOTS];
    uint8_t topologyCount;
    uint8_t slotCount;
} DEVICE_CONTEXT;


// Populate the DEVICE_CONTEXT structure with the valid topologies for the 
// device and the count of valid topologies
void IMG_MEM_FindValidTopologies(DEVICE_CONTEXT * ctx);

// Cache, validate, and sort headers from all firmware image slots for valid topologies
// Prerequisite: ctx initialized with FindValidTopologies
// Inputs:
//      ctx - A device context structure
//      buffer - A buffer for cached headers (HEADER_SIZE * MAX_SLOTS bytes)
void IMG_MEM_CacheAndValidateHeaders(DEVICE_CONTEXT * ctx, uint8_t * buffer);

// Cache a header from a firmware image slot
// Returns: Firmware image header pointer
// Inputs:
//      ctx - A context structure
//      top - Pointer to an image memory topology
//      pSlot - The image header slot to cache the header from
//      buffer - Pointer to a buffer in which to cache the header
//      bufSlot - Offset in the buffer in HEADER_SIZE units.  If a header is cached
//                  the contents of this pointer will be incremented by 1.
FW_IMG_HDR * IMG_MEM_CacheHeader(DEVICE_CONTEXT * ctx, 
    const IMG_MEM_TOPOLOGY * top, const SLOT_PARAMS * slot, 
    uint8_t * buffer, uint32_t * bufSlot);

// Validate a header
// Prerequisite: ctx initialized with FindValidTopologies
// Returns: true if valid, false otherwise
// Input: 
//      ctx - A device context structure
//      fwHdr Firmware image header pointer
// Criteria - Metadata revision, Sequence number (not 0 or 0xFFFFFFFF), rollback 
//              counter, image len % 4096 != 0, firmware and header auth method 
//              is ECDSA on P-384, encryption methods are None, Firmware image 
//              header is 0xE0 bytes, metadata container index is 1
bool IMG_MEM_ValidateHeader(DEVICE_CONTEXT * ctx, FW_IMG_HDR * fwHdr);

// Returns a topology based on a specific address
// Prerequisite: ctx initialized with FindValidTopologies
// Returns: topology pointer or NULL
// Inputs:
//      ctx - A device context structure
const IMG_MEM_TOPOLOGY * IMG_MEM_GetTopologyByAddress (DEVICE_CONTEXT * ctx, 
        uint32_t address);

// Sorts valid slots by priority
// Returns: None
// Inputs: A device context structure with cached and validated header pointers
//          in the header slots.
void IMG_MEM_SlotSort(DEVICE_CONTEXT * ctx);

// Begin a header authentication operation
// Inputs: 
//      digest - 48-byte buffer for the hash digest (maintain until authentication done)
//      ctx - A hash context (this must persist )
//      hdr - Pointer to a firmware image header
//      x - The x term of an ECDSA P-384 public key
//      y - The y term of an ECDSA P-384 public key
// Note: This function must not be called while the Public Key engine is in use.
bool IMG_MEM_AuthenticateHeaderStart(uint8_t * digest, FW_IMG_HDR * hdr, uint8_t * x, uint8_t * y);

// Check the status of a header authentication operation
// Prerequisite: Header authentication started with IMG_MEM_AuthenticateHeaderStart
// Returns: Success, failure, or busy (no result available)
// Inputs: None
AUTH_STATUS IMG_MEM_AuthenticateHeaderStatusGet(void);

#endif
