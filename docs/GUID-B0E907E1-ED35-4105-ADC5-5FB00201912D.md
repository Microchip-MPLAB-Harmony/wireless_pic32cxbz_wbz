# PDS_RegisterUpdateMemoryCallback Function

## C

```c
void PDS_RegisterUpdateMemoryCallback (bool (*callbackFn)(PDS_UpdateMemory_t *));
```

## Description

 This routine register the callback for the Item update memory.
 Updates BC parameters after restoring taking into account possible size

## Parameters

| Param | Description |
|:----- |:----------- |
| PDS_UpdateMemory_t | PDS_UpdateMemory_t |
| callbackFn | pointer to callback functions  

## Returns

 None. 

