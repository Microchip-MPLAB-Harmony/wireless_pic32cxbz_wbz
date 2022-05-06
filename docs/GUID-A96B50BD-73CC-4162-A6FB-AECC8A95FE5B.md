# DEVICE\_ClearDeepSleepReg Function

**Parent topic:**[Sleep System](GUID-BBF940E8-361C-4418-AA6E-7E55FE94DD87.md)

## C

```c
bool DEVICE_ClearDeepSleepReg(void);
```

## Description

The API is used to clear the deep sleep related register. If the device is waken from deep sleep mode, the related register will be cleared. If it's a normal Power-on Reset. no register will be cleared.

## Parameters

None

## Returns

A boolean value, True means the device is waken from deep sleep mode.

