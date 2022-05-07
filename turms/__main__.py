# =========================================
#   --- Turms ---
#   File transferring application
#   Made for COMP.SEC.300 course
#   in Tampere University, Spring 2022
#
#  Created by Sipi Ylä-Nojonen 2022
# -----------------------------------------

import application

def run():
    """
    Main function for setting up and running the application
    :return:
    """

    # Create logger for application

    # Create application window and run application
    app = application.App()
    application.call_async(app.run())
    return


if __name__ == '__main__':
    run()

