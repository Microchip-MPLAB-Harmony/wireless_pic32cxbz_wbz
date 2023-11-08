# PDS_MODULE_APP_OFFSET Function

## C

```c
#define PDS_MODULE_APP_OFFSET      (1 << 12)
```

The following offsets CAN be used(OR'ed) to define the range and also to differentiate
the module specific IDs, so the same item ID will not be used across the stacks/modules.

The IDs ranges are required to maintain the backward compatibility during an SW upgrade
with newly added item(s) in any module.

Note: These offset were not used anywhere inside PDS implementation(Library).
This is purely to enable the application to use specific IDs across modules.


