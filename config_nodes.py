﻿using System;
using System.IO;
using System.Text;

class ConfigNode():
    def __init__(self, name=None):
        if name is None:
            self.name = ''
        else:
            self.name = name

    def AddConfigNode(self, ):

class ConfigNodeReader():

    def string_to_config_node(self, inputString):
        inputString = inputString.split('\n')

        objectLevel = 0
        passName = ''
        passData = None
        current_line = None
        previous_line = None

        for line in inputString:
            trimmedLine = line.lstrip()

            # Take note of depth
            if trimmedLine == '{':
                objectLevel += 1
                # Started reading a config node block
                if objectLevel is 1:
                    passName = previous_line
                    passData = ''

            if trimmedLine == '}':
                objectLevel -= 1
                if objectLevel == 0:
                    # Finished reading a config node block
                    newNode = self.string_to_config_node(passData)
                    newNode.name = passName
                    returnNode.AddConfigNode(newNode);
                    passName = null;
                    passData = null;
                    continue;
                }
            }
            if (objectLevel == 0)
            {
                //We are reading a config node at our depth
                if (trimmedLine.Contains(" = "))
                {
                    string pairKey = trimmedLine.Substring(0, trimmedLine.IndexOf(" = "));
                    string pairValue = trimmedLine.Substring(trimmedLine.IndexOf(" = ") + 3);
                    returnNode.AddValue(pairKey, pairValue);
                }
            }
            else
            {
                //We are reading a different node
                passData.AppendLine(currentLine);
            }
            previousLine = trimmedLine;


        return returnNode
    }

    def file_to_config_node(self, inputFile)
        string configNodeText = File.ReadAllText(inputFile);
        return StringToConfigNode(configNodeText);