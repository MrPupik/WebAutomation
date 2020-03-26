import Autotest.Core.Logger as log
import subprocess

def processArgs(argList):
    """
    pass argument here and get dict with key-value, and list with flags. Usage: params, flags = process(sys.argv)
    """    
    params = {}
    flags = []
    if len(argList) > 0:
        for i in range(0,len(argList)-1):
            arg = str(argList[i])
            nArg = str(argList[i+1])
            if (arg.startswith('-') or arg.startswith('/')):
                if (nArg.startswith('-') or nArg.startswith('/')):
                    flags.append(arg)
                else:
                    params[arg] = nArg
        # if last one is a flag:
        arg = str(argList[-1])
        if (arg.startswith('-') or arg.startswith('/')):
            flags.append(arg)
    return (params, flags)

import types
import Autotest.Core.TimeoutManager as TimeoutManager
from time import sleep

def actionWrapper(action: types.FunctionType,
                  alternate=None,
                  fix_actions: list = None,
                  failTitle: str = "action failed",
                  *args):
    """
    wrap an action to be retried according to 'Lookup_options'.
    alternate[optional]: diffrent action with the same result (that gets the same *args).
    fix_actions[optional]: list of function to run bettween retries (1 at every retry)
    """
    total = 0
    attempt = 0
    timeout, sleep_time = TimeoutManager.Get()
    if not alternate:
        alternate = action

    while (total < timeout):
        try:
            err = None
            log.Quiet()
            if attempt % 2 == 0:
                return action(*args)
            else:
                return alternate(*args)

        except Exception as e:
            log.Noise()
            err = str(e)
            if attempt == 0:
                log.warn("core error: " + str(failTitle))
                log.info(err)
                log.std("\nretrying...")
            else:
                log.std(str(attempt)+"..")
            sleep(sleep_time)
            total += (sleep_time + TimeoutManager._implicit_wait)
            try:
                if fix_actions and len(fix_actions) > 0:
                    act = fix_actions[0]
                    log.std("[fix-"+str(act)[:35]+"]...")
                    log.Quiet()
                    act()
                    del fix_actions[0]
            except Exception as e:                            
                print("error at fix_action: "+str(e))
            finally:
                log.Noise()
        finally:
            log.Noise()
            attempt += 1
    if err:
        log.info(err)


def WaitForResult(Function, *args):
    """
    wait for Function to return a not-None value and returns it    
    *args - function args
    timeout - as defined at TimeoutManager
    """
    total = 0
    attempt = 0
    timeout, sleep_time = TimeoutManager.Get()
    log.info("WaitForResult "+str(Function))
    while (total < timeout):
        if attempt != 1:
            log.Quiet()
        result = Function(*args)
        if result:
            log.Noise()
            return result

        if attempt == 0:
            log.std("\nretrying...")
        else:
            log.std(str(attempt)+"..")
        sleep(sleep_time)
        total += (sleep_time + TimeoutManager._implicit_wait)
        attempt+=1
    log.Noise()
    return False




class Command( object ):
    def __init__( self, text ):
        self.text = text
    def execute( self ):
        print ("RUNNING: "+self.text)
        self.proc= subprocess.Popen(self.text)
        self.proc.wait()

class CommandSequence( Command ):
    def __init__( self, *steps ):
        self.steps = steps
    def execute( self ):
        for s in self.steps:
            s.execute()