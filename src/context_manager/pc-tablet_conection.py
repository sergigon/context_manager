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



# Exceptions
class TimeOut(Exception):
    pass

class PCTablet_Connection():
    """
    PC - Tablet Connection class.
    """

    # Global variables
    time_wait = 10 # sec

    def __init__(self):
        """
        Init method.
        """

        # Register the signal function handler
        signal.signal(signal.SIGALRM, self.handler)
        # Paths
        self._ssh_keys_path = "/home/user/.ssh/id_rsa.pub" # ssh keys path

        # Connection variables
        self._server, self._port, self._user = '10.42.0.34', 8022, 'u0_a156'

    def getSSHKeys(self):
        """
        Get the SSH keys.
        """

        file = open(self._ssh_keys_path, "r")
        key = file.read()
        return key

    def handler(self, signum, frame):
        """
        Register an handler for the timeout.
        """

        print "Forever is over!"
        raise TimeOut("end of time")

    def progress(self, filename, size, sent):
        """
        Define progress callback that prints the current percentage completed for the file.
        """

        # Global variables
        global filename_prev, sent_prev
        #sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
        print("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*10) )
        # Checks if it is stuck
        if(filename_prev!=filename or sent_prev!=sent): # It is not stuck
            signal.alarm(self.time_wait) # Restart timer
        # Fill prev variables
        filename_prev, sent_prev = filename, sent


    def createSSHClient(self):
        """
        Create SSH Client.
        """

        # Get ssh key
        key = self.getSSHKeys()

        # Establish ssh connection
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm

            # Create ssh object
            print('Create ssh object')
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self._server, self._port, self._user, key, banner_timeout=10)
            result = ssh
        # Exceptions
        except socket.error as e:
            print('socket.error: %s' % e)
            result = -1
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print('NoValidConnectionsError: %s ' % e)
            result = -1
        except paramiko.ssh_exception.SSHException as e:
            print('SSHException: %s' % e)
            result = -1
        except TimeOut as e: # TimeOut transfer)
            print('TimeOut: %s ' % e)
            result = -1

        if(result==-1):
            ssh.close()

        signal.alarm(0) # Disable the alarm
        return result

    def transferTablet2PC(self, remote_path, local_path, recursive = True):
        
        print('--- Tablet -> PC ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        
        result = 0
        # Transfer files 
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            # Create scp object
            print('Create scp object')
            scp = SCPClient(ssh.get_transport(), progress=progress)
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
            result = 0
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
        ssh.close()
        return result

    def transferPC2Tablet(self, local_path, remote_path, recursive = True):
        
        print('--- PC -> Tablet ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        
        result = 0
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            # Create scp object
            print('Create scp object')
            scp = SCPClient(ssh.get_transport(), progress=progress)
            # Put method
            print('Transfering files: %s -> %s' %(local_path, remote_path))
            global filename_prev, sent_prev
            filename_prev, sent_prev = '', 0
            print scp.put(local_path, recursive=recursive, remote_path=remote_path)
            # Close scp object
            print('Closing scp')
            scp.close()
            result = 0
        except OSError as e: # No PC file
            print('OSError: %s ' % e)
            result = -1
        except SCPException as e: # No tablet directory
            print('SCPException: %s ' % e)
            result = -1
        except TimeOut as e: # TimeOut transfer
            print ('TimeOut: %s ' % e)
            result = -1
        except EOFError as e: # EOFError transfer
            print ('EOFError: %s ' % e)
            result = -1
        
        signal.alarm(0) # Disable the alarm
        ssh.close()
        return result

    def lsTablet(self, direc = '.'):
        """
        Get the list of the files in a given directory.
        """
        print('--- lsTablet ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        
        result = 0
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            sftp = ssh.open_sftp()
            # listdir method
            print('ls to: %s' % direc)
            result = sftp.listdir(direc)

        except TimeOut as e: # TimeOut transfer
            print ('TimeOut: %s ' % e)
            result = -1
        except IOError as e: # Directory no exists
            print('IOError: %s ' % e)
            result = -1
        except paramiko.ssh_exception.SSHException as e:
            print ('SSHException: %s ' % e)
            result = -1
        else:
            print('ls made with success')
        signal.alarm(0) # Disable the alarm
        ssh.close()
        return result

    def mkdirTablet(self, direc):
        """
        Make a new directory in a given directory.
        """
        print('--- mkdirTablet ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        
        result = 0
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            sftp = ssh.open_sftp()
            # listdir method
            print('Creating directory: %s' % direc)
            result = sftp.mkdir(direc)

        except IOError as e: # Directory already exists or directory root no exists
            print('IOError: %s ' % e)
            result = -1
        except TimeOut as e: # TimeOut transfer
            print ('TimeOut: %s ' % e)
            result = -1
        except paramiko.ssh_exception.SSHException as e:
            print ('SSHException: %s ' % e)
            result = -1
        except paramiko.transport as e:
            print ('transport: %s ' % e)
            result = -1
        else:
            print('Directory created with success')

        signal.alarm(0) # Disable the alarm
        ssh.close()
        return result

    def existsTablet(self, direc):
        """
        Checks if a file or directory exists.
        """

        print('--- existsTablet ---')
        print('Checking: %s' % direc)

        # Get root directory
        direc_vec = direc.split('/')

        # Remove spaces
        direc_vec = [x for x in direc_vec if x != '']

        # Rebuild the directory
        direc = ''
        for folder in direc_vec[:-1]:
            direc = direc + '/' + folder
        file = direc_vec[-1]
        print('direc', direc)
        print('file', file)

        # Make ls
        list_files = self.lsTablet(direc)
        if(list_files == -1): # Directory error
            print ('Error')
            return -1

        # For to find it
        for list_files_i in list_files:
            if (list_files_i == file):
                print('File or directory found')
                return 0

        # Not found
        print('File or directory NOT found')
        return -2

    def cutTablet(self, oldpath, newpath):
        """
        Cut a new directory in a given directory.
        """

        print('--- cutTablet ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        result = 0
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            sftp = ssh.open_sftp()
            # listdir method
            print('Moving file %s to %s' % (oldpath, newpath))
            print sftp.rename(oldpath, newpath)
            result = 0
        except IOError as e: # Newpath is a folder or something goes wrong
            print('IOError: %s ' % e)
            result = -1
        except TimeOut as e: # TimeOut transfer
            print ('TimeOut: %s ' % e)
            result = -1
        except paramiko.ssh_exception.SSHException as e:
            print ('SSHException: %s ' % e)
            result = -1
        else:
            print('Directory created with success')

        signal.alarm(0) # Disable the alarm
        ssh.close()
        return result

    def removeTablet(self, path):
        """
        Cut a new directory in a given directory.
        """

        print('--- removeTablet ---')
        ssh = self.createSSHClient()
        if(ssh == -1):
            return -1
        result = 0
        try:
            print('Set alarm')
            signal.alarm(self.time_wait) # Start the alarm
            sftp = ssh.open_sftp()
            # listdir method
            print('Removing file %s' % path)
            print sftp.remove(path)
            result = 0
        except IOError as e: # Newpath is a folder or something goes wrong
            print('IOError: %s ' % e)
            result = -1
        except TimeOut as e: # TimeOut transfer
            print ('TimeOut: %s ' % e)
            result = -1
        except paramiko.ssh_exception.SSHException as e:
            print ('SSHException: %s ' % e)
            result = -1
        else:
            print('Directory removed with success')

        signal.alarm(0) # Disable the alarm
        ssh.close()
        return result


def loop_forever():
    import time
    while 1:
        print "sec"
        time.sleep(1)

# Main
if __name__ == '__main__':
    
    conector = PCTablet_Connection()
    print conector.removeTablet('/sdcard/multimedia/wikipedia/Source')
    #print conector.cutTablet('/sdcard/multimedia/Agumon.jpg', '/sdcard/multimedia/wikipedia/Agumon.jpg')
    print conector.cutTablet( '/sdcard/wikipedia/', '/sdcard/multimedia/wikipedia/')
    print conector.existsTablet('/sdcard/multimedia/Agumon.jp')
    print conector.lsTablet('/sdcard/multimedia/image/weather/wikipedia/g')
    print conector.mkdirTablet('/sdcard/multimedia/image/test/asd/gjjgy')
    '''
    print conector.createSSHClient()
    conector.transferPC2Tablet()
    '''

    #transferTablet2PC('/sdcard/multimedia/image/weather/wikipedia/', '/home/user/Documentos/')
    #conector.transferPC2Tablet('/home/user/Campeones.mp4', remote_path='/sdcard/multimedia/')
    #conector.transferPC2Tablet('/home/user/ROS/catkin_dev/src/time_weather_skill/data/weather_icons/wikipedia', remote_path='/sdcard/multimedia/')
    loop_forever()
