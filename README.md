# SecProg-FileTransfer-Turms
Exercise work for Secure Programming Course in Tampere University, Spring 2022

## Information - What is This?
Turms is a client-server model application for sharing files between users using HTTP(S) connection. It was created as an exercise work for 
Secure Programming Course in Tampere University, Spring 2022 in attempt to create an application following secure design principle and guides such
as OWASP top ten list of web application security risks.

## Installation and running the program
### **Windows** 
1. Ensure that you have Python 3.10.X installed from [Python Dowloads Page](https://www.python.org/downloads/).
2. Install required packages with 
´pip install <PACKAGE>==<VERSION>´.
The list of requirements can be found in [requirements.txt](https://github.com/SeipNojon-Tuni/SecProg-FileTransfer-Turms/requirements.txt)
3. Clone repository with
´git clone https://github.com/SeipNojon-Tuni/SecProg-FileTransfer-Turms.git´
4. Start application by running
´py <Path to project root>/turms/__main__.py´

## Usage
After application has started it can be used through Tkinter GUI. A configuration file will generated on start up if it doesn't exist in
´<Path to project root>/turms/config/config.cfg´
When running a server this can be used to define ip address for the server to determine the area network type for hosting.

