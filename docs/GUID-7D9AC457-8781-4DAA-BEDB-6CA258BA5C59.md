# PDS\_DECLARE\_ITEM Macro

**Parent topic:**[PDS Library Usage](GUID-A7B0958C-E476-48EA-9C30-DA83508CC577.md)

## C

```c
#define PDS_DECLARE_ITEM(item, size, pointer, func, flag) \
  PDS_FF_OBJECT(ItemIdToMemoryMapping_t pds_ff_##item) = \
    ITEM_ID_TO_MEM_MAPPING(item, size, pointer, func, flag);

```

## Description

PDS Declare Item Definition

To declare an itemfile in the PDS

item : Item ID \(Unique Indentifier number\)for that particular ItemFile

size: size of the item \(Maximum allowed size for an Item is 2K \(2048 Bytes\)

pointer: RAM address of the Item

func: filler function, can be set to NULL, \(will be called during the store operation\). Shall be kept to min size.

flag: NO\_ITEM\_FLAGS SIZE\_MODIFICATION\_ALLOWED ITEM\_UNDER\_SECURITY\_CONTROL

