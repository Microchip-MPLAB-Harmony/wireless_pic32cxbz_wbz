<#if ENABLE_DEEP_SLEEP == false>
    // Initialize the RF Clock Generator
    SYS_ClkGen_Config();

    // Configure Cache and Wait States
    PCHE_Setup();
</#if>
