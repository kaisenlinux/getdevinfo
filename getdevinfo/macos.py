#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# macOS Functions For The Device Information Obtainer
# This file is part of GetDevInfo.
# Copyright (C) 2013-2022 Hamish McIntyre-Bhatty
# GetDevInfo is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# GetDevInfo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GetDevInfo.  If not, see <http://www.gnu.org/licenses/>.

"""
This is the part of the package that contains the tools and information
getters for macOS. This would normally be called from the getdevinfo
module, but you can call it directly if you like.

.. note::
        You can import this submodule directly, but it might result
        in strange behaviour, or not work on your platform if you
        import the wrong one. That is not how the package is intended
        to be used, except if you want to use the get_block_size()
        function to get a block size, as documented below.

.. warning::
        Feel free to experiment, but be aware that you may be able to cause
        crashes, exceptions, and generally weird situations by calling
        these methods directly if you get it wrong. A good place to
        look if you're interested in this is the unit tests (in tests/).

.. warning::
        This module won't work properly unless it is executed as root.

.. module: macos.py
    :platform: macOS
    :synopsis: The part of the GetDevInfo module that houses the macOS
               tools.

.. moduleauthor:: Hamish McIntyre-Bhatty <support@hamishmb.com>

"""

import subprocess
import plistlib

#Define global variables to make pylint happy.
DISKINFO = None
PLIST = None
ERRORS = []

def get_info():
    """
    This function is the macOS-specific way of getting disk information.
    It makes use of the diskutil list, and diskutil info commands to gather
    information.

    It uses the other functions in this module to acheive its work, and
    it **doesn't** return the disk infomation. Instead, it is left as a
    global attribute in this module (DISKINFO).

    Raises:
        Nothing, hopefully, but errors have a small chance of propagation
        up to here here. Wrap it in a try:, except: block if you are worried.

    Usage:

    >>> get_info()
    """

    global DISKINFO
    DISKINFO = {}

    #Run diskutil list to get disk names.
    try:
        cmd = subprocess.run(["diskutil", "list", "-plist"], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, check=True)

    except (OSError, subprocess.CalledProcessError) as err:
        ERRORS.append("macos.get_info(): Exception: "+str(err)+" while running "
                      + "diskutil list\n")

        return

    else:
        #Get the output.
        #Keep this in bytes as plistlib.loads requires bytes (misleading function name)
        stdout = cmd.stdout

    #Parse the plist (Property List).
    global PLIST

    try:
        PLIST = plistlib.loads(stdout)

    except Exception as err:
        #TODO find which specific exceptions to handle, not in docs.
        ERRORS.append("macos.get_info(): Error parsing plist from diskutil list."
                      + " Output: " +stdout.decode("utf-8", errors="replace")+". Exception: "+str(err)+"\n")

        return

    #Find the disks.
    for disk in PLIST["AllDisks"]:
        #Run diskutil info to get disk info.
        try:
            cmd = subprocess.run(["diskutil", "info", "-plist", disk], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, check=True)

        except (OSError, subprocess.CalledProcessError) as err:
            ERRORS.append("macos.get_info(): Exception: "+str(err)+" while running "
                          + "diskutil info\n")

            continue

        else:
            #Get the output.
            #Keep this in bytes as plistlib.loads requires bytes (misleading function name)
            stdout = cmd.stdout

        #Parse the plist (Property List).
        try:
            PLIST = plistlib.loads(stdout)

        except Exception as err:
            #TODO find which specific exceptions to handle, not in docs.
            ERRORS.append("macos.get_info(): Error parsing plist from diskutil info."
                          + " Output: " +stdout.decode("utf-8", errors="replace")+". Exception: "+str(err)+"\n")

            continue

        #Check if the disk is a partition.
        disk_is_partition = is_partition(disk)

        if not disk_is_partition:
            #These are devices.
            get_device_info(disk)

        else:
            #These are Partitions. Fix for disks w/ more than 9 partitions.
            host_disk = "/dev/"+disk.split("s")[0]+"s"+disk.split("s")[1]
            get_partition_info(disk, host_disk)

    #Check we found some disks.
    if not DISKINFO:
        raise RuntimeError("No Disks found!")

def get_device_info(disk):
    """
    Private, implementation detail.

    This function gathers and assembles information for devices (whole disks).
    It employs some simple logic and the other functions defined in this
    module to do its work.

    Args:
        disk (str): The name of a device, without the leading /dev. eg: disk1

    Returns:
        string.     The name of the device.

    Usage:

    >>> host_disk = get_device_info(<aNode>)
    """

    host_disk = "/dev/"+disk
    DISKINFO[host_disk] = {}
    DISKINFO[host_disk]["Name"] = host_disk
    DISKINFO[host_disk]["Type"] = "Device"
    DISKINFO[host_disk]["HostDevice"] = "N/A"
    DISKINFO[host_disk]["Partitions"] = []
    DISKINFO[host_disk]["Vendor"] = get_vendor(disk)
    DISKINFO[host_disk]["Product"] = get_product(disk)
    DISKINFO[host_disk]["RawCapacity"], DISKINFO[host_disk]["Capacity"] = get_capacity()
    DISKINFO[host_disk]["Description"] = get_description(disk)
    DISKINFO[host_disk]["Flags"] = get_capabilities(disk)
    DISKINFO[host_disk]["Partitioning"] = get_partitioning(disk)
    DISKINFO[host_disk]["FileSystem"] = "N/A"
    DISKINFO[host_disk]["UUID"] = "N/A"
    DISKINFO[host_disk]["ID"] = get_id(disk)
    DISKINFO[host_disk]["BootRecord"], DISKINFO[host_disk]["BootRecordStrings"] = get_boot_record(disk)

    return host_disk

def get_partition_info(disk, host_disk):
    """
    Private, implementation detail.

    This function gathers and assembles information for partitions.
    It employs some simple logic and the other functions defined in this
    module to do its work.

    Args:
        disk (str):         The name of a partition, without the leading
                            /dev. eg: disk1s1

        host_disk (str):    The "parent" or "host" device. eg: for
                            /dev/disk1s1, the host disk would be /dev/disk1.
                            Used to organise everything nicely in the
                            disk info dictionary.

    Returns:
        string.     The name of the partition.

    Usage:

    >>> volume = get_device_info(<aDisk>, <aHostDisk>)
    """

    volume = "/dev/"+disk
    DISKINFO[volume] = {}
    DISKINFO[volume]["Name"] = volume
    DISKINFO[volume]["Type"] = "Partition"
    DISKINFO[volume]["HostDevice"] = host_disk
    DISKINFO[volume]["Partitions"] = []
    DISKINFO[host_disk]["Partitions"].append(volume)
    DISKINFO[volume]["Vendor"] = get_vendor(disk)
    DISKINFO[volume]["Product"] = "Host Device: "+DISKINFO[host_disk]["Product"]
    DISKINFO[volume]["RawCapacity"], DISKINFO[volume]["Capacity"] = get_capacity()
    DISKINFO[volume]["Description"] = get_description(disk)
    DISKINFO[volume]["Flags"] = get_capabilities(disk)
    DISKINFO[volume]["FileSystem"] = get_file_system(disk)
    DISKINFO[volume]["Partitioning"] = "N/A"
    DISKINFO[volume]["UUID"] = get_uuid(disk)
    DISKINFO[volume]["ID"] = get_id(disk)
    DISKINFO[volume]["BootRecord"], DISKINFO[volume]["BootRecordStrings"] = get_boot_record(disk)

    return volume

def is_partition(disk):
    """
    Private, implementation detail.

    This function determines if a disk is a partition or not.

    Args:
        disk (str):   Name of a device/partition.

    Returns:
        bool:

            - True  - Is a partition.
            - False - Not a partition.

    Usage:

    >>> is_a_partition = is_partition(<aDisk>)
    """

    return "s" in disk.split("disk")[1]

def get_vendor(disk):
    """
    Private, implementation detail.

    This function gets the vendor of the given disk.

    Args:
        disk (str):   Name of a device/partition.

    Returns:
        string. The vendor:

            - "Unknown"     - Couldn't find it.
            - Anything else - The vendor.

    Usage:

    >>> vendor = get_vendor(<aDisk>)
    """

    if DISKINFO["/dev/"+disk]["Type"] == "Partition":
        #We need to use the info from the host disk, which will be whatever came before.
        return DISKINFO[DISKINFO["/dev/"+disk]["HostDevice"]]["Vendor"]

    try:
        vendor = PLIST["MediaName"].split()[0]

    except KeyError:
        vendor = "Unknown"

    return vendor

def get_product(disk):
    """
    Private, implementation detail.

    This function gets the product of the given disk.

    Args:
        disk (str):   Name of a device/partition.

    Returns:
        string. The product:

            - "Unknown"     - Couldn't find it.
            - Anything else - The product.

    Usage:

    >>> product = get_product(<aDisk>)
    """

    if DISKINFO["/dev/"+disk]["Type"] == "Partition":
        #We need to use the info from the host disk, which will be whatever came before.
        return DISKINFO[DISKINFO["/dev/"+disk]["HostDevice"]]["Product"]

    try:
        product = ' '.join(PLIST["MediaName"].split()[1:])

    except KeyError:
        product = "Unknown"

    return product

def get_capacity():
    """
    Private, implementation detail.

    This function gets the capacity of the disk currently referenced in
    the diskutil info output we're storing. You can't really use this standalone.
    Also rounds it to a human-readable form, and returns both sizes.

    Returns:
        tuple (string, string). The sizes (bytes, human-readable):

            - ("Unknown", "Unknown")     - Couldn't find them.
            - Anything else              - The sizes.

    Usage:

    >>> raw_size, human_size = get_capacity()
    """

    try:
        raw_capacity = PLIST["TotalSize"]
        raw_capacity = str(raw_capacity)

    except KeyError:
        return "Unknown", "Unknown"

    #Round the sizes to make them human-readable.
    unit_list = [None, "B", "KB", "MB", "GB", "TB", "PB", "EB"]
    unit = "B"
    human_readable_size = int(raw_capacity)

    try:
        while len(str(human_readable_size)) > 3:
            #Shift up one unit.
            unit = unit_list[unit_list.index(unit)+1]
            human_readable_size = human_readable_size//1000

    except IndexError:
        return "Unknown", "Unknown"

    #Include the unit in the result for both exact and human-readable sizes.
    return raw_capacity, str(human_readable_size)+" "+unit

def get_description(disk):
    """
    Private, implementation detail.

    This function generates a human-readable description of the given disk.

    Args:
        disk (str):   Name of a device/partition.

    Returns:
        string. The description: This may contain various bits of info, or not,
                                 depending on what macOS knows about the disk.

    Usage:

    >>> description = get_description(<aDisk>)
    """
    #Gather info from diskutil to create some descriptions.
    # -- Internal or external --
    internal_or_external = "Unknown "

    if "Internal" in PLIST.keys():
        if PLIST["Internal"]:
            internal_or_external = "Internal "

        else:
            internal_or_external = "External "

    # -- Type: Removable, SSD, or HDD --
    disk_type = "Unknown "

    if ("Removable" in PLIST.keys() and PLIST['Removable']) or \
       ("RemovableMedia" in PLIST.keys() and PLIST['RemovableMedia']):
        disk_type = "Removable Drive "

    #Fix for old versions of OS X where the SolidState attribute is missing.
    #Means we assume things are HDDs if we can't otherwise figure them out.
    if disk_type == "Unknown " and "SolidState" in PLIST.keys() and PLIST["SolidState"]:
        disk_type = "Solid State Drive "

    elif disk_type == "Unknown ":
        disk_type = "Hard Disk Drive "

    # -- Bus protocol --
    bus_protocol = "Unknown"

    if "BusProtocol" in PLIST.keys():
        bus_protocol = str(PLIST["BusProtocol"])

    # -- APFS containers, volumes, physical stores --
    apfs_string = ""

    if "Content" in PLIST.keys() and PLIST["Content"] == "Apple_APFS":
        apfs_string = "(APFS Physical Store)"

    elif "APFSContainerReference" in PLIST.keys() and PLIST["APFSContainerReference"] == disk:
        apfs_string = "(APFS Container)"

    elif "FilesystemType" in PLIST.keys() and PLIST["FilesystemType"] == "apfs":
        apfs_string = "(APFS Volume)"

    #Assemble info into a string.
    if bus_protocol not in ("Unknown", "", " "):
        return internal_or_external+disk_type+"(Connected through "+bus_protocol+")"+apfs_string

    if disk_type != "Unknown ":
        return internal_or_external+disk_type+apfs_string

    if internal_or_external != "Unknown ":
        return internal_or_external+"Unknown Disk"+apfs_string

    return "N/A"

def get_capabilities(disk):
    """
    Not yet implemented, returns "Unknown"
    """

    #TODO
    return "Unknown"

def get_partitioning(disk):
    """
    Not yet implemented, returns "Unknown".
    """

    #TODO
    return "Unknown"

def get_file_system(disk):
    """
    Not yet implemented, returns "Unknown".
    """

    #TODO
    return "Unknown"

def get_uuid(disk):
    """
    Not yet implemented, returns "Unknown".
    """

    #TODO
    return "Unknown"

def get_id(disk):
    """
    Not yet implemented, returns "Unknown".
    """

    #TODO
    return "Unknown"

def get_boot_record(disk):
    """
    Not yet implemented, returns ("Unknown", "Unknown").
    """

    #TODO
    return "Unknown", "Unknown"

def get_block_size(disk):
    """
    **Public**

    .. note:
        It is perfectly safe to use this. The block size information
        is calculated on demand, rather that when collecting device
        information - just call this function with a device name to get
        the block size.

    This function uses the diskutil info command to get the block size
    of the given device.

    Args:
        disk (str):     The partition/device that
                        we want the block size for.

    Returns:
        int/None. The block size.

            - None - Failed!
            - int  - The block size.

    Usage:

    >>> block_size = get_block_size(<aDeviceName>)
    """

    #Run diskutil list to get disk names.
    command = ["diskutil", "info", "-plist", disk]

    try:
        cmd = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)

    except (OSError, subprocess.CalledProcessError) as err:
        ERRORS.append("macos.get_block_size(): Exception: "+str(err)+" while running "
                      + "diskutil info\n")

        return None

    else:
        #Get the output and pass it to compute_block_size.
        #Keep this in bytes as plistlib.loads requires bytes (misleading function name)
        return compute_block_size(disk, cmd.stdout)

def compute_block_size(disk, stdout):
    """
    Private, implementation detail.

    Used to process and tidy up the block size output from diskutil info.

    Args:
        stdout (str):       diskutil info's output.

    Returns:
        int/None: The block size:

            - None - Failed!
            - int  - The block size.

    Usage:

    >>> compute_block_size(<stdoutFromDiskutil>)
    """

    #Parse the plist (Property List).
    try:
        plist = plistlib.loads(stdout)

    except Exception as err:
        #TODO find which specific exceptions to handle, not in docs.
        ERRORS.append("macos.compute_block_size(): Error parsing plist from diskutil info."
                      + " Output: " +stdout.decode("utf-8", errors="replace")+". Exception: "+str(err)+"\n")

        return None

    else:
        if "DeviceBlockSize" in plist:
            result = str(plist["DeviceBlockSize"])

        elif "VolumeBlockSize" in plist:
            result = str(plist["VolumeBlockSize"])

        else:
            result = None

        return result
