__author__ = 'andrew.willis'

try:
    import crControllerUI
    reload (crControllerUI)
except:
    pass


try:
    import crControllerCore
    reload (crControllerCore)
except:
    pass

try:
    import crSetupCore
    reload (crSetupCore)
except:
    pass

try:
    import crSubmitCore
    reload (crSubmitCore)
except:
    pass

try:
    import crSetupConsole
    reload (crSetupConsole)
except:
    pass