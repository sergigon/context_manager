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

key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDJUBNBiHtJyRaKa+vcajQTWfwvJ/VbWX4Cquj3xkNPsfl0bFx4KUyFm1Oj3JmN/M4hH2KzCDCEnOIoqHA03pzSYpwgumUD3tUQ/Sv0+Y6tQ52KCyhCSSCe7o/mBWzry24Mov/sEC3zNLBCr7u/1nL3jzsbFKaRFAYqHQHz1Be+LZMW8aT+AqmxU76FLhJOI9EUj/8gaDs0xOXCPJWwTjQhxtXv/Qx5nFTWPLpS6mOAkpmr3VRbayGQGPHSN/WMuhrQjEn0wJgyX7OgywaNteXr2FEttRq2Xw9tqOd3v/c7shNhm6UYf4dggoTyDiXTd3M+/7WqUEEHG7kq22gPBWWnB6VazDv0YaxaOL/ahGAPHp4NJyKnt84AibUhs3mlDmnJphzPKvgSBzJftL5ZdSZtugNfq4LHyFdaM9qrTURT73txTTgLONzMkMiq/2pY9FPkwv6V1HfXZe0UTexH5a0/qq/SJk6oBOUpsVcvdz0mZoUpLgZr4v6EgHkv3KYBYprflzDdeyqVTIm29I6+29oB9ZbUmk1i+HCcDBYi+C0rbKYaIw0UZv9dARFL712uLoihfRFfTVIbMCA4YcSxrpnlIPI2dNiilvWzRPh4EBSZlViHE2cgoqwKiHMkVUEQeELybYTXs+iijL4ptAxf8cgRBTxG9q6ppHVsCAfzVU3+8Q== mini.uc3m@gmail.com'

import paramiko
from scp import SCPClient, SCPException
import rospy
import socket
import sys
import datetime
import signal # https://stackoverflow.com/questions/492519/timeout-on-a-function-call

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
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
    #print("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
    # Checks if it is stuck
    if(filename_prev!=filename and sent_prev!=sent): # It is not stuck
        # Restart timer
        signal.alarm(5)
    # Fill prev variables
    filename_prev = filename
    sent_prev = sent

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, banner_timeout=10)
    return client

def transferTablet2PC(remote_path, local_path, recursive = True):
    print('Tablet -> PC')
    # Establish connection
    try:
        # Create ssh object
        print('Create ssh object')
        ssh = createSSHClient('10.42.0.34', 8022, 'u0_a156', key)
        # Create scp object
        print('Create scp object')
        scp = SCPClient(ssh.get_transport(), progress=progress)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        rospy.logerr('NoValidConnectionsError: %s ' % e)
        print ('NoValidConnectionsError: %s ' % e)
        return -1
    except socket.error as e:
        rospy.logerr('%s' % e)
        print e
        return -1
    except paramiko.ssh_exception.SSHException as e:
        rospy.logerr('%s' % e)
        print e
        return -1
    # Transfer files
    try:
        print('Transfering files')
        global filename_prev, sent_prev
        filename_prev, sent_prev = '', 0
        print('Set alarm')
        # Register the signal function handler
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5) # Start the alarm
        # Get method
        scp.get(remote_path, local_path, recursive = True)
        signal.alarm(0) # Disable the alarm
    except SCPException as e: # No tablet file
        rospy.logerr('SCPException: %s ' % e)
        print ('SCPException: %s ' % e)
    except IOError as e: # No PC directory
        rospy.logerr('IOError: %s ' % e)
        print ('IOError: %s ' % e)
    except TimeOut as e: # TimeOut transfer
        rospy.logerr('TimeOut: %s ' % e)
        print ('TimeOut: %s ' % e)
    # Close scp object
    scp.close()

def transferPC2Tablet(local_path, remote_path, recursive = True):
    print('PC -> Tablet')
    # Establish connection
    try:
        # Create ssh object
        print('Create ssh object')
        ssh = createSSHClient('10.42.0.34', 8022, 'u0_a156', key)
        # Create scp object
        print('Create scp object')
        scp = SCPClient(ssh.get_transport(), progress=progress)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        rospy.logerr('NoValidConnectionsError: %s ' % e)
        print ('NoValidConnectionsError: %s ' % e)
        return -1
    except socket.error as e:
        rospy.logerr('%s' % e)
        print e
        return -1
    except paramiko.ssh_exception.SSHException as e:
        rospy.logerr('%s' % e)
        print e
        return -1
    # Transfer files
    try:
        print('Transfering files')
        global filename_prev, sent_prev
        filename_prev, sent_prev = '', 0
        print('Set alarm')
        # Register the signal function handler
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(5) # Start the alarm
        # Put method
        print scp.put(local_path, recursive=recursive, remote_path=remote_path)
        signal.alarm(0) # Disable the alarm
    except OSError as e: # No PC file
        rospy.logerr('%s' % e)
    except SCPException as e: # No tablet directory
        rospy.logerr('%s' % e)
        print e
    except TimeOut as e: # TimeOut transfer
        rospy.logerr('TimeOut: %s ' % e)
        print ('TimeOut: %s ' % e)
    # Close scp object
    scp.close()

def getPassword():
    pass


def loop_forever():
    import time
    while 1:
        print "sec"
        time.sleep(1)




# Main
if __name__ == '__main__':
    print('hola\r')
    print('aaaaa\r')
    transferTablet2PC('/sdcard/multimedia/image/weather/wikipedia/', '/home/user/Documentos/')

    loop_forever()

    try:
        # Register the signal function handler
        signal.signal(signal.SIGALRM, handler)
        ssh = createSSHClient('10.42.0.34', 8022, 'u0_a156', key)
        scp = SCPClient(ssh.get_transport(), progress=progress)
        rospy.sleep(5)
        print 'eeee'
        '''
        ftp_client = ssh.open_sftp()
        ftp_client.get('/sdcard/multimedia/Agumon.jpg','/home/user/Documentos/Agu.png')
        ftp_client.close()
        ftp_client.close()
        '''
        # Tablet - PC
        print('Tablet - PC')
        try:
            try:
                print('Get method')
                filename_prev = ''
                sent_prev = 0
                print('Set alarm')
                #signal.alarm(3)
                scp.get('/sdcard/multimedia/image/weather/wikipedia/', '/home/user/Documentos/', recursive = True, preserve_times=True)
            except GeneralError, exc:
                print '[General Error]: %s' % exc
            print('Disable alarm')
            signal.alarm(0)          # Disable the alarm
            loop_forever()

        except SCPException as e: # No tablet file
            rospy.logerr('SCPException: %s ' % e)
            print ('SCPException: %s ' % e)
        except IOError as e: # No PC directory
            rospy.logerr('IOError: %s ' % e)
            print ('IOError: %s ' % e)
        except GeneralError as e:
            rospy.logerr('GeneralError: %s ' % e)
            print ('GeneralError: %s ' % e)

        # PC - Tablet
        print('PC - Tablet')
        try:
            print('Put method')
            print scp.put('/home/user/Agumon.jpg', recursive=True, remote_path='/sdcard/multimedia/a/')
        except OSError as e: # No PC file
            rospy.logerr('%s' % e)
        except SCPException as e: # No tablet directory
            rospy.logerr('%s' % e)
            print e
        
        scp.close()
    except socket.error as e:
        rospy.logerr('%s' % e)
        print e
    except paramiko.ssh_exception.SSHException as e:
        rospy.logerr('%s' % e)
        print e

