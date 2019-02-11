#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Sergio Gonzalez Diaz"
__copyright__ = "Social Robots Group. Robotics Lab. University Carlos III of Madrid"
__credits__ = ["Sergio Gonzalez Diaz"]
__license__ = "LEUC3M v1.0"
__version__ = "0.0.0"
__maintainer__ = "Sergio Gonzalez Diaz"
__email__ = "sergigon@ing.uc3m.es"
__status__ = "Development"

'''from paramiko import SSHClient
from scp import SCPClient

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('example.com')

# SCPCLient takes a paramiko transport as an argument
scp = SCPClient(ssh.get_transport())

scp.put('test.txt', 'test2.txt')
scp.get('test2.txt')

# Uploading the 'test' directory with its content in the
# '/home/user/dump' remote directory
scp.put('test', recursive=True, remote_path='/home/user/dump')

scp.close()'''

#key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDJUBNBiHtJyRaKa+vcajQTWfwvJ/VbWX4Cquj3xkNPsfl0bFx4KUyFm1Oj3JmN/M4hH2KzCDCEnOIoqHA03pzSYpwgumUD3tUQ/Sv0+Y6tQ52KCyhCSSCe7o/mBWzry24Mov/sEC3zNLBCr7u/1nL3jzsbFKaRFAYqHQHz1Be+LZMW8aT+AqmxU76FLhJOI9EUj/8gaDs0xOXCPJWwTjQhxtXv/Qx5nFTWPLpS6mOAkpmr3VRbayGQGPHSN/WMuhrQjEn0wJgyX7OgywaNteXr2FEttRq2Xw9tqOd3v/c7shNhm6UYf4dggoTyDiXTd3M+/7WqUEEHG7kq22gPBWWnB6VazDv0YaxaOL/ahGAPHp4NJyKnt84AibUhs3mlDmnJphzPKvgSBzJftL5ZdSZtugNfq4LHyFdaM9qrTURT73txTTgLONzMkMiq/2pY9FPkwv6V1HfXZe0UTexH5a0/qq/SJk6oBOUpsVcvdz0mZoUpLgZr4v6EgHkv3KYBYprflzDdeyqVTIm29I6+29oB9ZbUmk1i+HCcDBYi+C0rbKYaIw0UZv9dARFL712uLoihfRFfTVIbMCA4YcSxrpnlIPI2dNiilvWzRPh4EBSZlViHE2cgoqwKiHMkVUEQeELybYTXs+iijL4ptAxf8cgRBTxG9q6ppHVsCAfzVU3+8Q== mini.uc3m@gmail.com'

import paramiko
from scp import SCPClient, SCPException
import rospy
import socket
import sys
import datetime
import signal # https://stackoverflow.com/questions/492519/timeout-on-a-function-call

# Global variables
time_wait = 10 # sec

# Exceptions
class TimeOut(Exception):
    pass

# Register an handler for the timeout
def handler(signum, frame):
    print "Forever is over!"
    raise TimeOut("end of time")

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    # Global variables
    global filename_prev, sent_prev
    #sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
    print("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
    # Checks if it is stuck
    if(filename_prev!=filename or sent_prev!=sent): # It is not stuck
        # Restart timer
        print('restart')
        signal.alarm(time_wait)
        
    # Fill prev variables
    filename_prev = filename
    sent_prev = sent

def getPassword():
    file = open("/home/user/.ssh/id_rsa.pub", "r")
    key = file.read()
    return key

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, banner_timeout=10)
    return client

def createSSHClient_control():
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)
    # Get ssh key
    key = getPassword()
    # Establish ssh connection
    try:
        print('Set alarm')
        signal.alarm(time_wait) # Start the alarm
        # Create ssh object
        print('Create ssh object')
        ssh = createSSHClient('10.42.0.34', 8022, 'u0_a156', key)
    except socket.error as e:
        print('socket.error: %s' % e)
        signal.alarm(0) # Disable the alarm
        return -1
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print('NoValidConnectionsError: %s ' % e)
        signal.alarm(0) # Disable the alarm
        return -1
    except paramiko.ssh_exception.SSHException as e:
        print('SSHException: %s' % e)
        signal.alarm(0) # Disable the alarm
        return -1
    except TimeOut as e: # TimeOut transfer)
        print('TimeOut: %s ' % e)
        signal.alarm(0) # Disable the alarm
        return -1
    signal.alarm(0) # Disable the alarm
    return ssh # Success

def transferTablet2PC(remote_path, local_path, recursive = True):
    ssh = createSSHClient_control()
    if(ssh == -1):
        return -1
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)
    print('Tablet -> PC')
    result = 0
    # Transfer files 
    try:
        # Create scp object
        print('Create scp object')
        scp = SCPClient(ssh.get_transport(), progress=progress)
        print('Set alarm')
        signal.alarm(time_wait) # Start the alarm
        # Get method
        print('Transfering files: %s -> %s' %(remote_path, local_path))
        global filename_prev, sent_prev
        filename_prev, sent_prev = '', 0
        scp.get(remote_path, local_path, recursive = True)
        #ftp_client = ssh.open_sftp()
        #ftp_client.get('/sdcard/multimedia/Agumon.jpg','/home/user/Documentos/Agu.png')
        # Close scp object
        print('Closing scp')
        scp.close()
    except SCPException as e: # No tablet file
        print('SCPException: %s ' % e)
        result = -1
    except IOError as e: # No PC directory
        print ('IOError: %s ' % e)
        result = -1
    except TimeOut as e: # TimeOut transfer
        print ('TimeOut: %s ' % e)
        result = -1
    signal.alarm(0) # Disable the alarm
    return result

def transferPC2Tablet(local_path, remote_path, recursive = True):
    ssh = createSSHClient_control()
    if(ssh == -1):
        return -1
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)
    print('PC -> Tablet')
    result = 0
    try:
        # Create scp object
        print('Create scp object')
        scp = SCPClient(ssh.get_transport(), progress=progress)
        print('Set alarm')
        signal.alarm(time_wait) # Start the alarm
        # Put method
        print('Transfering files: %s -> %s' %(local_path, remote_path))
        global filename_prev, sent_prev
        filename_prev, sent_prev = '', 0
        print scp.put(local_path, recursive=recursive, remote_path=remote_path)
        # Close scp object
        print('Closing scp')
        scp.close()
    except OSError as e: # No PC file
        print('OSError: %s ' % e)
        result = -1
    except SCPException as e: # No tablet directory
        print('SCPException: %s ' % e)
        result = -1
    except TimeOut as e: # TimeOut transfer
        print ('TimeOut: %s ' % e)
        result = -1
    except EOFError as e: # TimeOut transfer
        print ('EOFError: %s ' % e)
        result = -1
    signal.alarm(0) # Disable the alarm
    return result

def loop_forever():
    import time
    while 1:
        print "sec"
        time.sleep(1)

# Main
if __name__ == '__main__':
    
    #transferTablet2PC('/sdcard/multimedia/image/weather/wikipedia/', '/home/user/Documentos/')
    transferPC2Tablet('/home/user/Campeones.mp4', remote_path='/sdcard/multimedia/')
    transferPC2Tablet('/home/user/ROS/catkin_dev/src/time_weather_skill/data/weather_icons/wikipedia', remote_path='/sdcard/multimedia/')
    loop_forever()
