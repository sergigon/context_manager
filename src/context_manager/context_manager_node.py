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

import rospkg
import rospy
import rosparam
import sys

import datetime
import requests

import yaml # https://pyyaml.org/wiki/PyYAMLDocumentation

# Skill variables
# Package name
pkg_name = 'context_manager'

# Local paths
rospack = rospkg.RosPack()
pkg_path = rospack.get_path(pkg_name) + '/' # Package path
path_data = pkg_path + 'data/'

if __name__ == '__main__':
    try:
        # start the node
        rospy.init_node(pkg_name, log_level=rospy.DEBUG)
        rospy.loginfo('[' + pkg_name + ']')

        print "Número de argumentos: ", len(sys.argv)
        print "Lista de argumentos: ", sys.argv

        n_user = 0

        n_user = int(raw_input('\nIntroduce el numero de tu usuario (0, 1, 2, 3): '))

        # User
        filename_user = 'user' + str(n_user) +'.yaml'
        filename_robot = 'robot.yaml'
        pathfile_user = path_data + filename_user
        pathfile_robot = path_data + filename_robot

        try:
            stream_user = file(pathfile_user, 'r')
            stream_robot = file(pathfile_robot, 'r')
        except IOError as e:
            rospy.logerr(e)
        user = yaml.load(stream_user)
        robot = yaml.load(stream_robot)

        # Context
        context = {
            'user': user,
            'robot': robot
        }
        
        # Set context
        rospy.set_param('context', context)
        
        # Print parameters
        print('Context:')
        print(rosparam.get_param('context'))
        print('')
        print(type(rospy.get_param('context/user/birth_date')))
        print('')
        print(rospy.get_param('context/user/surname'))
        print('')

    except rospy.ROSInterruptException:
        pass
