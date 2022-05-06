# PDS\_RegisterUpdateMemoryCallback Function

**Parent topic:**[PDS Library Usage](GUID-A7B0958C-E476-48EA-9C30-DA83508CC577.md)

## C

```c
void PDS_RegisterUpdateMemoryCallback (bool (*callbackFn)(PDS_UpdateMemory_t *));
```

## Description

This routine register the callback for the Item update memory. Updates BC parameters after restoring taking into account possible size

## Parameters

|Param|Description|
|-----|-----------|
|PDS\_UpdateMemory\_t|PDS\_UpdateMemory\_t|
|callbackFn|pointer to callback functions|

## Returns

None.

