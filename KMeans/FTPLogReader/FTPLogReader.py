import re
import os.path
import logging
import datetime
from time import ctime


__author__ = "Caleb Whitman"
__version__ = "1.0.0"
__email__ = "calebrwhitman@gmail.com"

"""Parses a vsftpd logfile and outputs a tensor representing the file.
   In order to use the FTPLogReader, instantiate a new class and then call getConnectionTensors to get the tensors."""
class FTPLogReader:

    """ Instanitates a new FTPLogReader.
        Args:
            file (string): The vsftpd logfile to read from.
            position (int): The position to start reading the file. Defaults to start of file.
            logFile (string): The logfile that any errors will be logged to. Defaults to FTPParseLog.log"""
    def __init__(self,file,position =0,logFile="FTPParseLog.log" ):
        if( not os.path.isfile(file)):
            raise IOError("File not found.")
        logging.basicConfig(filename=logFile, level=logging.WARNING)
        logging.getLogger().addHandler(logging.StreamHandler())
        self.file =file
        self.position = position

    """ Returns tensors from the logfile representing the connection information.
         Returns:
            [ [4] ]: A list of connections. Each list contains all connections for a particular IP address."""
    def getConnectionTensors(self):
        dict = self.__parseLogFile__()
        conn_dict = self.__getConnections__(dict)
        ips = self.__sortByIP__(conn_dict)
        ips_int = self.__convertToTensor__(ips)
        for key in ips:
            yield ips_int[key]

    """Parses the logfile and returns a list of dictionaries representing every line.
        Returns:
            [{}]: A list of dictionaries representing the logfile."""
    def __parseLogFile__(self):

        #Open file and go to the correct staring position.
        fp = open(self.file, 'r')
        fp.seek(self.position,0)
        result = []

        #Read and parse each line.
        for line in fp:
            try:
                result.append(self.__parseLine__(line))
            except CantParseException:
                logging.warning("%s: Line unable to be parsed: %s"%(ctime(),line))

        #Get end of file position
        self.position=fp.tell()
        #Close file pointer
        fp.close()
        return result

    """ Looks through the dictionaries and filters out any that do not represent a connection.
         Args:
                dictinaries ([{}]): The list of dictionaries representing the ftp log.
        Returns:
            [{}]: A list of dictionaries representing connections and connection attempts.
            """
    def __getConnections__(self,dictionaries):

        result=[]
        for dict in dictionaries:
            if(dict["status"]=="CONNECT" or dict["status"]=="OK LOGIN" or dict["status"]=="FAIL LOGIN"):
                result.append(dict)

        return result



    """ Sorts the list of dictionaries by IP addresses.
         Args:
                dictinaries ([{}]): The list of dictionaries representing the ftp log.
        Returns:
            {ip:[{}]}: A dictionary holding each list of dictionaries for a given ip.
            """
    def __sortByIP__(self,dictionaries):
        result = {}
        for dict in dictionaries:
            if dict["ip"] in result:
                result[dict["ip"]].append(dict)
            else:
                result[dict["ip"]]=[dict]
        return result

    """ Converts all dictionaries into a list for processing.
             Args:
                    dictionaries {ip:[{}]}: The list of dictionaries representing the ip addresses.
            Returns:
                {ip:[[]]}: A dictionary holding the list representing the tensor for that ip.
                """
    def __convertToTensor__(self, ips):

        for key in ips:
            tensor = ips[key]
            new_tensor=[]
            for dict in tensor:
                inner_list=[]
                inner_list.append(dict["status"])
                username = dict["username"]
                if username is None:
                    username = ""
                inner_list.append(username)
                inner_list.append(dict["ip"])
                inner_list.append(str(unix_time_seconds(dict["datetime"])))
                new_tensor.append(inner_list)
            ips[key]=new_tensor

        return ips



    """ Parses the line and returns a dictionary representing that line.
        Returns:
            {}: A dictionary in the format {datetime,pid,username,status,ip,parameters}
            -datetime is a datetime object representing the time the action occured.
            -pid is the process id on the server.
            -username is the user name that carried out the connection. May be None.
            -status is the status of the connection.
            -ip is the ip address of the client.
            -parameters is a string containing a comma seperated list of parameters. May be None.
            """
    def __parseLine__(self,line):
        logPattern = r"" \
                     r"([^ ]*) " \
                     r"([^ ]*) " \
                     r"([^ ]*) " \
                     r"([^ ]*) " \
                     r"([^ ]*) " \
                     r"(\[[^\[]*\]) " \
                     r"(\[[^\[]*\] )?" \
                     r"([^:]*): " \
                     r"Client \"([^\"]*)\"" \
                     r",? ?(.+)?"
        compiledPattern = re.compile(logPattern)
        matched = compiledPattern.match(line)
        if (matched is None):
            raise CantParseException
        else:
            #Do further parsing on any of the components and then put the result into the dictionary
            groups = matched.groups()
            months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
            time = groups[3].split(":")
            date = datetime.datetime(int(groups[4]), months[groups[1]], int(groups[2]), int(time[0]), int(time[1]), int(time[2]))
            if groups[6] is not None:
                username = groups[6].replace("[","").replace("]","")
            else:
                username=None

            resultDictionary = {"datetime": date, "pid": groups[5], "username": username, "status": groups[7],
                                "ip": groups[8], "parameters": groups[9]}

        return resultDictionary

    """Parses the parameters into a dictionary. Each dictionary will hold a different value depending on the parameter format.
        Parameters that are not reconized are not returned.
        Currently only parses out the the parameter "PORT 123,123 etc...."
        Args:
            params (string): A comma seperated listed of paraemters
     Param: params, the parameters in a comma seperated string format."""
    def __parseParameter__(params):
        if (params is None):
            return
        returnDictionary = {}
        # Ports
        portsParam = r"\"PORT ([0-9]*,?)*\""
        compiledPattern = re.compile(portsParam)
        matched = compiledPattern.match(params)
        if (matched is not None):
            group = matched.group(0)
            portRemove = group.split()
            ports = portRemove[1].split(",")
            portNums = []
            [portNums.append(int(x.replace("\"", ""))) for x in ports[1:]]
            returnDictionary["PORT"] = portNums

        return returnDictionary


"""Gets the time in seconds from the given datetime."""
def unix_time_seconds(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()

"""Thrown when we read in a line we can't parse."""
class CantParseException(Exception):
    pass
