'''
Created on 27/08/2013

This is where you do your work.
Not only do you need to fill in the methods but you can also add any other classes, 
methods or functions to this file to make your system pass all of the tests.

@author: qzhu496
'''
import os
import math
from drive import Drive

class A2File(object):
    '''
    One of these gets returned from Volume open.
    ''' 
    fileName = ""
    fileSize = 0

    def __init__(self, filename):
        '''
        Initializes an A2File object.
        Not called from the test file but you should call this from the
        Volume.open method.
        You can use as many parameters as you need.
        '''
        fileName = filename
    
    def size(self):
        '''
        Returns the size of the file in bytes.
        '''
        return self.fileSize
    
    def write(self, location, data):
        '''
        Writes data to a file at a specific byte location.
        If location is greater than the size of the file the file is extended
        to the location with spaces. 
        '''
        pass
    
    def read(self, location, amount):
        '''
        Reads from a file at a specific byte location.
        An exception is thrown if any of the range from
        location to (location + amount - 1) is outside the range of the file.
        Areas within the range of the file return spaces if they have not been written to.
        '''
        pass

class Volume(object):
    '''
    A volume is the disk as it appears to the file system.
    The disk structure is to be entirely stored in ASCII so that it
    can be inspected easily. It must contain:
        Volume data blocks: the number of contiguous blocks with the volume data - as a string, ends with "\n"
        Name: at least one character plus "\n" for end of name)
        Size: as a string terminated with "\n"
        Free block bitmap: drive.num_blocks() + 1 bytes ("x" indicates used, "-" indicates free, ends with "\n")
        First block of root directory (called root_index) : as a string terminated with "\n" - always the last
            block on the drive.
    '''

    @staticmethod
    def format(drive, name):
        '''
        Creates a new volume in a disk.
        Puts the initial metadata on the disk.
        The name must be at least one byte long and not include "\n".
        Raises an IOError if after the allocation of the volume information
        there are not enough blocks to allocate the root directory and at least
        one block for a file.
        Returns the volume.
        '''
        if not name.decode():
            raise ValueError("file name is empty")
        if "\n" in name.decode():
            raise ValueError("file name includes new line character")
        if len(name.decode()) >= drive.num_bytes():
            raise ValueError("file name is longer than vailable spaces")

        volume = Volume()
        volume.drive_name = drive.name
        volume.blocksOccupied = 1
        volume.BLK_SIZE = drive.BLK_SIZE
        volume.volumeName = name
        volume.numberOfBlocks = drive.num_blocks()
        volume.bitmapStr = 'x' + '-' * (volume.numberOfBlocks - 2) + 'x'
        volume.rootDirIndex = drive.num_blocks() - 1
        def getOutput(self):
            return (str(self.blocksOccupied) + "\n" + (self.volumeName).decode() + "\n" + 
                str(self.numberOfBlocks) + "\n" + self.bitmapStr + "\n" + str(volume.rootDirIndex) + "\n")
        volume.blocksOccupied = math.ceil(len(getOutput(volume)) / drive.BLK_SIZE)
        for i in range(volume.blocksOccupied):
            # if i > 0 and i < volume.numberOfBlocks:
            volume.bitmapStr = volume.bitmapStr[:i] + 'x' + volume.bitmapStr[i+1:]
            drive.write_block(i, getOutput(volume).encode()[i * volume.BLK_SIZE : i * volume.BLK_SIZE + volume.BLK_SIZE].ljust(drive.BLK_SIZE))
        
        drive.write_block(volume.numberOfBlocks - 1, ('  0\n' * 16).encode().ljust(drive.BLK_SIZE))
        return volume


    
    def name(self):
        '''
        Returns the volumes name.
        '''
        return self.volumeName
        
    
    def volume_data_blocks(self):
        '''
        Returns the number of blocks at the beginning of the drive which are used to hold
        the volume information.
        '''
        return self.blocksOccupied
        
    def size(self):
        '''
        Returns the number of blocks in the underlying drive.
        '''
        return self.numberOfBlocks
    
    def bitmap(self):
        '''
        Returns the volume block bitmap.
        '''
        return self.bitmapStr.encode()
    
    def root_index(self):
        '''
        Returns the block number of the first block of the root directory.
        Always the last block on the drive.
        '''
        return self.numberOfBlocks - 1
    
    @staticmethod
    def mount(drive_name):
        '''
        Reconnects a drive as a volume.
        Any data on the drive is preserved.
        Returns the volume.
        '''
        # if not os.path.exists(drive_name):
        #     raise IOError('file does not exist')
        volume = Volume()
        drive = Drive.reconnect(drive_name)

        '''
        volume.volumeName = name    # should i include '\n' or not?
        volume.numberOfBlocks = drive.num_blocks()
        volume.bitmapStr = 'x' + '-' * (volume.numberOfBlocks - 2) + 'x'
        '''

        volume.drive_name = drive.name
        volume.blocksOccupied = int(drive.read_block(0).split()[0].decode())
        volumeInfoByte = bytearray()
        for i in range(volume.blocksOccupied):
            volumeInfoByte += (drive.read_block(i))
        volume.fileName = drive_name
        volumeInfoStr = volumeInfoByte.decode().split('\n')
        volume.volumeName = volumeInfoStr[1].encode()
        volume.numberOfBlocks = int(volumeInfoStr[2])
        volume.bitmapStr = volumeInfoStr[3]
        volume.rootDirIndex = volumeInfoStr[4]

        return volume
    
    def unmount(self):
        '''
        Unmounts the volume and disconnects the drive.
        '''
        pass
    def rootFileList(self):
        drive = Drive.reconnect(self.drive_name)
        fileMapBytes = drive.read_block(drive.num_blocks() -1 )
        fileMapIndex = [int(s) for s in fileMapBytes.decode().split() if (s.isdigit() and s != '0' ) ]
        fileInfoByte = bytearray()
        for i in fileMapIndex:
            fileInfoByte += drive.read_block(i)

        fileInfoStr = fileInfoByte.decode()
        fileList = [s.strip() for s in fileInfoByte.decode().split("\n") if not s.isdigit()]
        # print("fileInfoByte: " + fileInfoByte.decode())
        print("fileList: " + str(fileList))
        # for s in fileMapBytes.decode().split('\n') :
        #     if s.isdigit() : print(str(s))
        return fileList
    
    def open(self, filename):
        '''
        Opens a file for read and write operations.
        If the file does not exist it is created.
        Returns an A2File object.
        '''

        if not filename.decode():
            raise ValueError("file name is empty")
        if "\n" in filename.decode():
            raise ValueError("file name includes new line character")

        # if not os.path.exists(filename):
        self.rootFileList()
        file = A2File(filename)
        #open(filename, 'w+')
        return file