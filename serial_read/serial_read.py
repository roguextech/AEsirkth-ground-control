"""
Class to read data sent over serial link and save it on storage

"""

import csv
import datetime
from os import mkdir
from os.path import isdir, join

import serial
import serial.tools.list_ports

bonjour = "TELEMETRY"  # Not used


class Telemetry:
    """ Class to read data received via serial link

    The data read from the serial link is stored in a CSV file in real time
    The system time of receiving each line is stored along the received data
    in ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)

    Parameters
    ----------
    baudrate : int
        Baurate of the serial link
    path : path-like object
        Path to the file to write
        File extension should be '.csv'
    port : string
        Full name/path of the port the instance is set to read data from
    is_reading : bool
        True if the instance is currently reading data from serial link

    Examples
    --------
    >>> telemetry = Telemetry(baudrate=115200, path="path/to/file.csv")
    >>> port = telemetry.find_serial(bonjour="TELEMETRY")
    >>> telemetry.start_read()
    ...
    >>> telemetry.stop_read()


    >>> telemetry = Telemetry(baudrate=115200, path="path/to/file.cvs")
    >>> telemetry.start_read(bonjour="TELEMETRY")
    ...
    >>> telemetry.stop_read()

    """

    separators = {
        'START_HEAD': '@',
        'START_DATA': '#',
        'START_CALI': '%',
        'START_MESS': '$',
        'SEP_DATA': '&',
        'SEP_CALI': ':',
        'END_LINE': '\n'
    }

    # We need to do searches both ways...
    separators_reversed = {value: key for key, value in separators.items()}

    def __init__(self, baudrate, path):
        self.baudrate = baudrate
        self.path = path
        self.is_reading = False
        self.port = ""
        self.header = ""
        self.calibration = {}
        self.messages = []
        self.data = [[], [], [],]
        self.date_created = datetime.datetime.now().replace(microsecond=0).isoformat()
        self.data_file = "{}_data.csv".format(self.date_created.replace(":","-"))
        self.data_path = join(self.path, self.data_file)

        if not isdir(self.path):
            mkdir(self.path)
        
        with open(self.data_path, 'w'):
            print("Data file created")

    def write_data(self, dataArray):
        """ Append a line in the file located at `self.data_path`

        Each element of `dataArray` is written separated by a comma ','

        Parameters
        ----------
        dataArray: array-like object
            data to write in the file

        """
        with open(self.data_path, 'a+', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(dataArray)

    def get_clean_serial_line(self, ser):
        """ Read a line from serial link and return it as a string

        The line is decoded to ascii and the newline character is removed

        NB: The newline character is different on linux systems

        Parameters
        ----------
        ser : Serial instance
            the Serial instance to read a line from

        Returns
        -------
        line : string
            the processed line read from serial

        """
        line = ser.readline()
        line = line.decode('ascii')
        line = line.replace(self.separators['END_LINE'], "")
        return line

    def process_header(self, line):
        # Don't write the header twice
        if not self.header:
            self.header = ["Time"] + line.split(self.separators['SEP_DATA'])
            self.write_data(self.header)
            print("Header : {}".format(self.header))

    def process_data(self, line):
        """ Save data in memory and on file storage

        Parameters
        ----------
        line : string
            line received from telemetry, without start and end character

        """
        if self.header:
            now = datetime.datetime.now().isoformat()
            data = [now] + line.split(self.separators['SEP_DATA'])
            # Need to make this append at the exact same time
            if not self.data[0]:
                self.data[0] = [data[0]]
            else:
                self.data[0].append(data[0])
            if not self.data[1]:
                self.data[1] = [int(data[1])]
            else:
                self.data[1].append(int(data[1]))
            if not self.data[2]:
                self.data[2] = [int(data[2])]
            else:
                self.data[2].append(int(data[2]))
            self.write_data(data)

    def process_calibration(self, line):
        """ Save calibration data in memory

        Parameters
        ----------
        line : string
            line received from telemetry, without start and end character

        """
        # Don't save the calibration twice
        if not self.calibration:
            self.calibration = {value.split(self.separators['SEP_CALI'])[0]: value.split(
                self.separators['SEP_CALI'])[1] for value in line.split(self.separators['SEP_DATA'])}
            print("Got calibration")
            print("Calibration data : {}".format(self.calibration))

    def process_message(self, line):
        """ Save a message line in memory

        Parameters
        ----------
        line : string
            line received from telemetry, without start and end character

        """
        self.messages += line
        print("Message : {}".format(line))

    def process_line(self, line):
        if len(line) > 0:
            line_start = line[0]
            line_content = line[1:]
            if line_start in self.separators_reversed:
                line_type = self.separators_reversed[line_start]

                if line_type == 'START_DATA':
                    self.process_data(line_content)

                elif line_type == 'START_HEAD':
                    self.process_header(line_content)

                elif line_type == 'START_CALI':
                    self.process_calibration(line_content)

                elif line_type == 'START_MESS':
                    self.process_message(line_content)

    def find_serial(self, bonjour):
        """ Test all connected serial devices to find the one that sends `bonjour` as the first transmitted line

        `self.port` is updated when the device is successfully found. It is set to `None` otherwise

        Parameters
        ----------
        bonjour : string
            string that should be sent by the device we want to find

        Returns
        -------
        port : string
            full name/path of the port where the found device is connected
            None is returned if the device is not found

        """
        available_ports = serial.tools.list_ports.comports()

        print("\nSearching for available serial devices...")
        print("Found device(s) : {}".format(
            ", ".join([p.description for p in available_ports])))

        for p in available_ports:
            print("Testing : {}...".format(p.device))
            # The timeout should be long enough to that the telemetry receiver can reset and send BONJOUR before the reading ends
            with serial.Serial(p.device, baudrate=self.baudrate, timeout=2) as ser:
                ser.reset_input_buffer()

                line = self.get_clean_serial_line(ser)

                if line == bonjour:
                    print("Found telemetry device on port : {}".format(p.device))
                    self.port = p.device
                    return p.device

        print("/!\\ Failed to find telemetry device /!\\")
        # Must trigger an exception instead of returning None
        self.port = None
        return None

    def start_read(self, bonjour=None):
        """ Wait to get a valid header via serial link then save all received data to a file

        Does not stop until stop_read() is called

        Parameters
        ----------
        bonjour : string, optional
            string that should be sent by the device we want to find

        """
        self.is_reading = True
        self.data = [[], [], [],]

        # If `bonjour` is given, search for the device location
        # If not, don't search for the device and assume that `self.port` is already set correctly
        if bonjour != None:
            self.find_serial(bonjour)

        # NB: need to find a way to catch timeouts
        with serial.Serial(self.port, baudrate=self.baudrate, timeout=0.1) as ser:

            ser.reset_input_buffer()  # Reset the buffer

            while self.is_reading:
                line = self.get_clean_serial_line(ser)
                self.process_line(line)

    def stop_read(self):
        """" Call this method to terminate serial reading

        Call start_read() to start the reading again

        """
        self.is_reading = False
