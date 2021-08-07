# GPIO 25 - Encoder A for Motor1
# GPIO 22 - Encoder B for Motor1
# GPIO 24 - Encoder A for Motor2
# GPIO 23 - Encoder B for Motor2
import os
import sys
import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

import Libraries.Thunderborg as ThunderBorg

TB = ThunderBorg.ThunderBorg()   # Create a new ThunderBorg object
TB.i2cAddress = 10               # Uncomment and change the value if you have changed the board address
TB.Init()                        # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print('No ThunderBorg found, check you are attached :)')
    else:
        print(f'No ThunderBorg at address {TB.i2cAddress}, but we did find boards:')
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so it is correct, e.g.')
        print('TB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()

TB.MotorsOff()
