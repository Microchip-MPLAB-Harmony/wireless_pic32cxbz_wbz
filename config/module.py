######################  Harmony wireless_pic32cxbz_wbz  ######################
def loadModule():
    print('Load Module: Harmony Wireless PIC32CXBZ_WBZ')

    pic32cx_bz2_family = {'PIC32CX1012BZ25048',
                          'PIC32CX1012BZ25032',
                          'PIC32CX1012BZ24032',
                          'WBZ451',
                          'WBZ450',
                          }

    pic32cx_bz3_family = {'PIC32CX5109BZ31048',
                          'PIC32CX5109BZ31032',
                          'WBZ435',
                          }
    processor = Variables.get('__PROCESSOR')
    print('processor={}'.format(processor))

    if( processor in pic32cx_bz2_family):
        ## PIC32CX-BZ System_Service
        execfile(Module.getPath() + '/config/module_pic32cx_bz2_device_support.py')
        ## Persistant Data Storage
        execfile(Module.getPath() + '/config/module_pic32cx_bz_pds.py')
        ## PIC32CX-BZ Bootloader
        execfile(Module.getPath() + '/config/module_pic32cx_bz2_bootloader.py')
        ## PIC32CX-BZ OTA
        execfile(Module.getPath() + '/config/module_pic32cx_bz2_bootloaderServices.py')

    elif( processor in pic32cx_bz3_family):
        ## PIC32CX-BZ System_Service
        execfile(Module.getPath() + '/config/module_pic32cx_bz3_device_support.py')
        ## Persistant Data Storage
        execfile(Module.getPath() + '/config/module_pic32cx_bz_pds.py')
        execfile(Module.getPath() + '/config/module_pic32cx_bz3_signFW.py')