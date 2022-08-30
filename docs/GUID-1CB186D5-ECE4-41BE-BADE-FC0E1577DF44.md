# OSAL_QUEUE_SelectFromSet Function

## C

```c
OSAL_RESULT OSAL_QUEUE_SelectFromSet(OSAL_QUEUE_SET_MEMBER_HANDLE_TYPE *queSetMember, OSAL_QUEUE_SET_HANDLE_TYPE *queSetID, uint16_t waitMS);
```

## Description

 Block to wait for something to be available from the queues or semaphore that have been added to the set.

## Parameters

| Param | Description |
|:----- |:----------- |
| queSetMember | Member queue or semaphore to be added in the set |
| queSetID | A pointer to the queue ID |
| waitMS | wait time in milliseconds. other value OSAL_WAIT_FOREVER  

## Returns

*OSAL_RESULT_TRUE* - A queue had been created

*OSAL_RESULT_FALSE* - Queue creation failed


