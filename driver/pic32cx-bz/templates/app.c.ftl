<#assign BLESTACK_OR_ZIGBEESTACK_LOADED = (BLESTACK_LOADED) || (ZIGBEESTACK_LOADED)>
/*******************************************************************************
  MPLAB Harmony Application Source File

  Company:
    Microchip Technology Inc.

  File Name:
    app.c

  Summary:
    This file contains the source code for the MPLAB Harmony application.

  Description:
    This file contains the source code for the MPLAB Harmony application.  It
    implements the logic of the application's state machine and it may call
    API routines of other MPLAB Harmony modules in the system, such as drivers,
    system services, and middleware.  However, it does not call any of the
    system interfaces (such as the "Initialize" and "Tasks" functions) of any of
    the modules in the system or make any assumptions about when those functions
    are called.  That is the responsibility of the configuration-specific system
    files.
 *******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
#include <string.h>
#include "app.h"
#include "definitions.h"
<#if BLESTACK_LOADED>
#include "app_ble.h"
<#if ENABLE_DEEP_SLEEP>
#include "app_ble_dsadv.h"
</#if>
</#if>
<#if ZIGBEESTACK_LOADED>
#include "app_zigbee/app_zigbee.h"
#include <zigbee_device/common/include/z3Device.h>
#include <zigbee_device/api/include/zgb_api.h>
#include <zigbee_device/api/include/bdb_api.h>
#include <osal/osal_freertos.h>
</#if>


// *****************************************************************************
// *****************************************************************************
// Section: Global Data Definitions
// *****************************************************************************
// *****************************************************************************
<#if ZIGBEESTACK_LOADED && (ENABLE_CONSOLE == true) >
extern void process_UART_evt(char* cmdBuf);
extern void APP_UartInit(void);
extern void APP_UartHandler(void);
</#if>
<#if ZIGBEESTACK_LOADED>
extern void process_ZB_evt(void);
extern void ZB_ZCL_CallBack(ZB_AppGenericCallbackParam_t* cb);
extern ZDO_CALLBACK_ptr ZB_ZDO_CallBack[];
</#if>

// *****************************************************************************
/* Application Data

  Summary:
    Holds application data

  Description:
    This structure holds the application's data.

  Remarks:
    This structure should be initialized by the APP_Initialize function.

    Application strings and buffers are be defined outside this structure.
*/

APP_DATA appData;

// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************

/* TODO:  Add any necessary callback functions.
*/

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************


/* TODO:  Add any necessary local functions.
*/


// *****************************************************************************
// *****************************************************************************
// Section: Application Initialization and State Machine Functions
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void APP_Initialize ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Initialize ( void )
{
    /* Place the App state machine in its initial state. */
    appData.state = APP_STATE_INIT;


    appData.appQueue = xQueueCreate( 64, sizeof(APP_Msg_T) );
    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
<#if ZIGBEESTACK_LOADED && (ENABLE_CONSOLE == true) >
    APP_UartInit();
</#if>
<#if ZIGBEESTACK_LOADED>

    APP_ZigbeeStackInit();
</#if>
}


/******************************************************************************
  Function:
    void APP_Tasks ( void )

  Remarks:
    See prototype in app.h.
 */

void APP_Tasks ( void )
{
    APP_Msg_T    appMsg[1];
<#if BLESTACK_OR_ZIGBEESTACK_LOADED>
    APP_Msg_T   *p_appMsg;
    p_appMsg=appMsg;
</#if>

<#if ZIGBEESTACK_LOADED>
    ZB_AppGenericCallbackParam_t cb;
</#if>
    /* Check the application's current state. */
    switch ( appData.state )
    {
        /* Application's initial state. */
        case APP_STATE_INIT:
        {
            bool appInitialized = true;
            //appData.appQueue = xQueueCreate( 10, sizeof(APP_Msg_T) );
<#if BLESTACK_LOADED>
            <#if ENABLE_DEEP_SLEEP == false>
            APP_BleStackInit();
            <#if SLEEP_SUPPORTED>
            RTC_Timer32Start();
            </#if>            
            <#else>
            bool flag=false;

            flag=APP_BleDsadvIsEnable();

            if (flag == false)
            {
                APP_BleStackInit();
                APP_BleDsadvStart(flag);
                <#if SLEEP_SUPPORTED>
                RTC_Timer32Start();
                </#if>
            }
            else   //Wake up from deep sleep by RTC/INT0/Watch dog
            {
                 APP_BleDsadvStart(flag);
            }
            </#if>
</#if>
<#if SLEEP_SUPPORTED && BLESTACK_LOADED == false>
            RTC_Timer32Start();
</#if>

            if (appInitialized)
            {

                appData.state = APP_STATE_SERVICE_TASKS;
            }
            break;
        }

        case APP_STATE_SERVICE_TASKS:
        {
            if (OSAL_QUEUE_Receive(&appData.appQueue, &appMsg, OSAL_WAIT_FOREVER))
            {
<#if BLESTACK_LOADED>
                if(p_appMsg->msgId==APP_MSG_BLE_STACK_EVT)
                {
                    // Pass BLE Stack Event Message to User Application for handling
                    APP_BleStackEvtHandler((STACK_Event_T *)p_appMsg->msgData);
                }
                else if(p_appMsg->msgId==APP_MSG_BLE_STACK_LOG)
                {
                    // Pass BLE LOG Event Message to User Application for handling
                    APP_BleStackLogHandler((BT_SYS_LogEvent_T *)p_appMsg->msgData);
                }
</#if>
<#if ZIGBEESTACK_LOADED>
                if (p_appMsg->msgId == APP_MSG_ZB_STACK_CB)
                {
                    // Pass Zigbee Stack Callback Event Message to User Application for handling
                    uint32_t *paramPtr = NULL;
                    memcpy(&paramPtr,p_appMsg->msgData,sizeof(paramPtr));
                    memcpy(&cb, paramPtr, sizeof(cb));
                    switch (cb.eModuleID)
                    {
                      case ZIGBEE_BDB:
                        ZB_BDB_CallBack(&cb);
                      break;

                      case ZIGBEE_ZDO:
                        ZB_ZDO_CallBack[cb.uCallBackID]((void *)cb.parameters);
                      break;

                      case ZIGBEE_ZCL:
                          ZB_ZCL_CallBack(&cb);
                      break;

                      default:
                        //appSnprintf("[APP CB]  Default case\r\n");
                      break;
                    }
                    void *ptr = NULL;
                    memcpy(&ptr, p_appMsg->msgData,sizeof(ptr));
                    OSAL_Free(ptr);
                    OSAL_Free(cb.parameters);
                    
                }
                else if(p_appMsg->msgId==APP_MSG_ZB_STACK_EVT)
                {
                    // Pass Zigbee Stack Event Message to User Application for handling
                    process_ZB_evt();
                }
</#if>
<#if (ZIGBEESTACK_LOADED && (ENABLE_CONSOLE == true))>
                else if( p_appMsg->msgId == APP_MSG_UART_CMD_READY)
                {
                    process_UART_evt((char*)(p_appMsg->msgData));
                }
</#if>
            }
            break;
        }

        /* TODO: implement your application state machine.*/


        /* The default state should never be executed. */
        default:
        {
            /* TODO: Handle error in application's state machine. */
            break;
        }
    }
}


/*******************************************************************************
 End of File
 */