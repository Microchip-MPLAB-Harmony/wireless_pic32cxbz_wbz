# DEVICE\_CONTEXT Struct

**Parent topic:**[Bootloader API Usage](GUID-9B3F465C-7297-4547-B7C6-3AAABEB7E261.md)

## C

```c
typedef struct
{
    // Valid Toplogies
    const IMG_MEM_TOPOLOGY *     validTops[MAX_MEM_TOPOLOGIES];
    // Valid slots information
    VALID_SLOT                   validSlots[MAX_SLOTS];
    // Number of Topologies
    uint8_t topologyCount;
    // Number of slots
    uint8_t slotCount;
} DEVICE_CONTEXT;

```

## Description

Defines the device context information ie., valid tops and valid slots

