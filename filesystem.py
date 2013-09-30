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
    content_byte = b''

    def __init__(self, filename, fileMapBytesIndex, size=0):
        '''
        Initializes an A2File object.
        Not called from the test file but you should call this from the
        Volume.open method.
        You can use as many parameters as you need.
        '''
        self.fileName = filename
        self.fileMapBytesIndex = fileMapBytesIndex
        self.fileSize = size

    def toString(self):
        string = "fileName: {} size: {} fileMapBytesIndex: {} content is empty: {}".format(
            self.fileName, self.fileSize, self.fileMapBytesIndex, self.content_byte==b'')
        return string
    
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
        # self.fileSize += len(data)
        self.content_byte = self.content_byte[:location] + b' ' * ((location - self.fileSize) if location > self.size() else 0) + data + self.content_byte[location:]
        self.fileSize = len(self.content_byte)
        # print("self.content_byte: " + self.content_byte.decode())
        # if location 
        pass
    
    def read(self, location, amount):
        '''
        Reads from a file at a specific byte location.
        An exception is thrown if any of the range from
        location to (location + amount - 1) is outside the range of the file.
        Areas within the range of the file return spaces if they have not been written to.
        '''
        print("read file: " + self.fileName.decode() + " size: " + str(self.size()) + " content: " + str(self.content_byte))
        if (location + amount - 1) > self.size():
            raise IOError("out of bound")
        print("reading file location: " + str(location) + " amount: " + str(amount))
        return self.content_byte[location:location + amount]

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
    def read_map(self, n, input_type_is_file = False):
        mapInt = [int(s) for s in self.drive.read_block(n).decode().split() if (s.isdigit() and s != '0' ) ]
        # if return_type == "mapInt": return mapInt
        content_byte = bytearray()
        for i in mapInt:
            if input_type_is_file == True:
                # print("deleting block: " + str(i))
                self.bitmapStr = self.bitmapStr[:i] + '-' + self.bitmapStr[i+1:]
                # self.drive.write_block(i, b' ' * self.drive.BLK_SIZE)
            content_byte += self.drive.read_block(i)
        # print("read_map: \n    mapInt: " + str(mapInt) + "    content_byte: " + str(content_byte))
        return content_byte

    def write_map(self, root_files_block_index, index=[]):
        # print("writting map: root_files_block_index: " + str(root_files_block_index) + " : " + str(index))
        data = bytearray()
        for i in index:
            data += '{:' '>3}\n'.format(i).encode()
        data += ('  0\n' * 18).encode()
        # print("writting map: " + str(data))
        # data = data[:self.drive.BLK_SIZE]
        # print("writing map to block: " + str(n) + " content: " + str(data))
        # self.drive.write_block(root_files_block_index, data)
        for i, mapInt in enumerate(root_files_block_index):
            print("writting map: i: " + str(i) + " " + str(data[i * self.BLK_SIZE : (i+1) * self.BLK_SIZE].ljust(self.BLK_SIZE)))
            self.drive.write_block(mapInt, data[i * self.BLK_SIZE : (i+1) * self.BLK_SIZE].ljust(self.BLK_SIZE))
    def read_block_info(self):
        volumeInfoByte = bytearray()
        for i in range(self.block_info_occupied_blocks_num):
            volumeInfoByte += (self.drive.read_block(i))
        return volumeInfoByte
    def write_block_info(self):
        # print("write_block_info: bitmap: " + self.bitmapStr)
        # self.block_info_occupied_blocks_num = 
        for i in range(self.block_info_occupied_blocks_num):
            # print("write_block_info: to block: " + str(i) + " with: " + str(self.get_first_block_str().encode()[i * self.BLK_SIZE : i * self.BLK_SIZE + self.BLK_SIZE].ljust(self.BLK_SIZE)))
            self.drive.write_block(i, self.get_first_block_str().encode()[i * self.BLK_SIZE : i * self.BLK_SIZE + self.BLK_SIZE].ljust(self.BLK_SIZE))
        
        

    def get_first_block_str(self):
        string = (str(self.block_info_occupied_blocks_num) + "\n" + (self.volume_name).decode() + "\n" + 
            str(self.size()) + "\n" + self.bitmapStr + "\n" )
        string2 = ""
        for i in self.root_files_block_index:
            string2 += str(i) + " "
        print("get_first_block_str string2: " + string2)
        # + str(self.root_files_block_index) + "\n"
        # print("get_first_block_str string: " + string)
        return string + string2

    def retriveAvailableBlock(self):
        availableBlockIndex = self.bitmapStr.find('-')
        # print("found space at: " + str(availableBlockIndex) + " current bitmapStr: " + self.bitmapStr)
        if (availableBlockIndex) == -1 : 
                raise IOError("disk out of space")
                return 
        else :
            self.bitmapStr = self.bitmapStr[:availableBlockIndex] + 'x' + self.bitmapStr[availableBlockIndex+1:]
            return availableBlockIndex

    def get_root_file_list(self):
        print("get_root_file_list root_files_block_index: " + str(self.root_files_block_index))
        fileList = []
        # TODO:
        content_byte = bytearray()
        for i in self.root_files_block_index:
            content_byte += self.read_map(self, i)
        # mapInt = [int(s) for s in self.drive.read_block(self.root_index()).decode().split() if (s.isdigit() and s != '0' ) ]
        # content_byte = bytearray()
        # for i in mapInt:
        #     content_byte += self.drive.read_block(i)
        # print("read_map: \n    mapInt: " + str(mapInt) + "    content_byte: " + str(content_byte))
        fileInfoStr = [s.strip() for s in content_byte.decode().split("\n") if s.strip() != ""]
        # print("fileInfoStr in get_root_file_list: " + str(fileInfoStr) + " len: " + str(len(fileInfoStr)))
        for i in list(range(0,len(fileInfoStr),3)):
            if fileInfoStr[i].strip() != '':
                fileName = fileInfoStr[i]
                i+=1
                fileSize = fileInfoStr[i]
                i+=1
                fileMapBytesIndex = int(fileInfoStr[i])
                file = A2File(fileName.encode(), fileMapBytesIndex, int(fileSize))
                # print("adding new file to fileList: " + str(file.fileName) + " empty?" + str(file.content_byte.decode() == "") + " size: " + str(file.fileSize)) 
                fileList.append(file)
        # print("fileList: " + (str(i.fileName) + " ") for i in fileList )
        for i in fileList: print("      fileList: " + str(i.fileName) + " file_index: " + str(i.fileMapBytesIndex), end="")
        return fileList
    def write_file_list(self):
        root_file_info_byte = bytearray()
        root_file_occupied_block_list = []
        for i in self.rootFileList:
            root_file_info_byte+=(i.fileName+("\n"+str(i.fileSize)+"\n"+str(i.fileMapBytesIndex)+"\n").encode())
        # TODO:
        root_files_required_num_of_blocks = math.ceil(len(root_file_info_byte) / self.drive.BLK_SIZE)
        for i in range(math.ceil(root_files_required_num_of_blocks / (self.BLK_SIZE / 4)) - len(self.root_files_block_index)):
            self.root_files_block_index.append(self.retriveAvailableBlock())
        root_file_occupied_block_list = [self.retriveAvailableBlock() for i in list(range(root_files_required_num_of_blocks))]
        # write maps in last block
        # for i, 
        # self.write_map(self.root_files_block_index, root_file_occupied_block_list)
        for i in list(range((root_files_required_num_of_blocks))):
            print("writing files info to block: " + str(root_file_occupied_block_list[i]))#str(root_files_required_num_of_blocks))
            self.drive.write_block(root_file_occupied_block_list[i], root_file_info_byte[i * self.BLK_SIZE : (i + 1) * self.BLK_SIZE].ljust(self.BLK_SIZE))
        print("write_file_list - root_file_occupied_block_list: " + str(root_file_occupied_block_list))
        self.write_map(self.root_files_block_index, root_file_occupied_block_list)
        pass
    def open_file(self, file):
        content = bytearray()
        content_byte = self.read_map(self, file.fileMapBytesIndex, True)
        file.content_byte = content_byte
        return file
        # delete content bitmap


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
        print("\nformating volume: " + str(name))
        if not name.decode():
            raise ValueError("file name is empty")
        if "\n" in name.decode():
            raise ValueError("file name includes new line character")
        if len(name.decode()) >= drive.num_bytes():
            raise ValueError("file name is longer than vailable spaces")

        volume = Volume()
        # volume.drive_name = drive.name
        # int
        volume.block_info_occupied_blocks_num = 1
        # int
        volume.BLK_SIZE = drive.BLK_SIZE
        # byte
        volume.volume_name = name
        # int
        volume.total_num_of_blocks = drive.num_blocks()
        # str
        volume.bitmapStr = 'x' + '-' * (volume.total_num_of_blocks - 2) + 'x'
        # int
        volume.root_files_block_index = [drive.num_blocks() - 1]
        # array
        volume.rootFileList = []
        volume.openingFiles = []
        # drive
        volume.drive = drive
        volume.block_info_occupied_blocks_num = math.ceil(len(volume.get_first_block_str()) / drive.BLK_SIZE)
        volume.bitmapStr = 'x' * volume.block_info_occupied_blocks_num + '-' * (volume.total_num_of_blocks - 1 - volume.block_info_occupied_blocks_num) + 'x'
        volume.write_block_info()
        volume.write_map(volume.root_files_block_index)
        return volume
    
    def name(self):
        '''
        Returns the volumes name.
        '''
        return self.volume_name
        
    
    def volume_data_blocks(self):
        '''
        Returns the number of blocks at the beginning of the drive which are used to hold
        the volume information.
        '''
        return self.block_info_occupied_blocks_num
        
    def size(self):
        '''
        Returns the number of blocks in the underlying drive.
        '''
        return self.total_num_of_blocks
    
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
        return self.root_files_block_index[0]

    @staticmethod
    def mount(drive_name):
        '''
        Reconnects a drive as a volume.
        Any data on the drive is preserved.
        Returns the volume.
        '''
        print("mounting volume: " + str(drive_name))

        volume = Volume()
        volume.drive = Drive.reconnect(drive_name)
        # volume.drive_name = drive.name
        # int
        volume.block_info_occupied_blocks_num = int(volume.drive.read_block(0).split()[0].decode())
        # int
        volume.BLK_SIZE = volume.drive.BLK_SIZE
        # print("mounting: " + str(volume.drive.read_block(0)))
        volumeInfoByte = volume.read_block_info()
        volumeInfoStr = volumeInfoByte.decode().split('\n')

        # volume.volumeName = volumeInfoStr[1].encode()
        # volume.numberOfBlocks = int(volumeInfoStr[2])
        # volume.bitmapStr = volumeInfoStr[3]
        # volume.rootDirIndex = int(volumeInfoStr[4])
        # volume.rootFileList = volume.getRootFileList()
        # volume.openingFiles = []
        print("volumeInfoStr: " + str(volumeInfoStr))
        # byte
        volume.volume_name = volumeInfoStr[1].encode()
        # int
        volume.total_num_of_blocks = int(volumeInfoStr[2])
        # str
        volume.bitmapStr = volumeInfoStr[3]
        print("mounting volume with bitmap: " + volume.bitmapStr)
        # int int(volumeInfoStr[4]) [s.strip() for s in content_byte.decode().split("\n") if s.strip() != ""]
        volume.root_files_block_index = [int(i) for i in volumeInfoStr[4].split() if i.strip() != "" and i.isdigit()]
        print("root_files_block_index: " + str(volume.root_files_block_index))
        # array
        volume.rootFileList = volume.get_root_file_list()
        volume.openingFiles = []
        return volume
    
    def unmount(self):
        '''
        Unmounts the volume and disconnects the drive.
        '''
        print("unmounting volume: " + str(self.volume_name))
        # write files to disk
        for i in self.openingFiles:
            block_required = math.ceil(len(i.content_byte) / self.drive.BLK_SIZE)
            blocksOccupiedMapIndex = []
            # blocksOccupiedMapIndex = [int(s) for i in range(blocksRequired) : s = self.bitmapStr.find('-') ]
            for j in range(block_required):
                availableBlockIndex = self.retriveAvailableBlock()
                blocksOccupiedMapIndex.append(availableBlockIndex)
                data = i.content_byte[j * self.drive.BLK_SIZE : (j + 1) * self.drive.BLK_SIZE ].ljust(self.drive.BLK_SIZE)
                self.drive.write_block(availableBlockIndex, data)
            # filesInfoBytes+=(i.fileName+("\n"+str(i.fileSize)+"\n"+str(i.fileMapBytesIndex)+"\n").encode())
            print("writing file to disk: " + i.toString() )
            self.write_map([i.fileMapBytesIndex], blocksOccupiedMapIndex)
        #write file list to disk
        # print("current bitmap: " + self.bitmapStr)
        self.write_file_list()
        # print("current bitmap: " + self.bitmapStr)
        self.write_block_info()
        self.drive.file.flush()
        print("unmounted volume: " + str(self.volume_name) + " current bitmap: " + self.bitmapStr)

        pass
    
    def open(self, filename):
        '''
        Opens a file for read and write operations.
        If the file does not exist it is created.
        Returns an A2File object.
        '''
        print("opening file: " + str(filename))
        if not filename.decode():
            raise ValueError("file name is empty")
        if "\n" in filename.decode():
            raise ValueError("file name includes new line character")
        if "/" in filename.decode():
            raise ValueError("does not support subdirectory yet")

        # check if the file is opened:
        for i in self.openingFiles:
            if i.fileName == filename:
                print("find file already opened: " + str(filename))
                return i
        # if the file is already exist
        for i in self.rootFileList:
            if i.fileName == filename:
                print("find file already existing: " + str(filename))
                return self.open_file(i)
        # create new file:
        file = A2File(filename, self.retriveAvailableBlock())
        print("creating new file: " + str(file.fileName))
        self.rootFileList.append(file)
        self.openingFiles.append(file)
        return file
