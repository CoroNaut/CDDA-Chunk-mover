# CDDA Chunk mover
import os
import json
import math


def main():
    print("\nWelcome to CDDA Chunk mover")
    print("There is a 5 step process")

    savedir = None
    save_dir_List = []
    save_sav_list = []

    while savedir == None:
        savedir = input("1. Enter full path to CDDA save directory: ")
        print("\n")

        save_dir_List = getDirs(savedir)
        if len(save_dir_List) == 0:
            print("Path doesn't have any saves")
            continue

        # get list of .sav files and store into saveList
        for dir in save_dir_List:
            sav_file = getSave(dir)

            if not sav_file:
                print("No save file found in: ", os.path.basename(dir))
                save_dir_List.remove(dir)
            else:
                save_sav_list.append(os.path.basename(dir))

        # Check if we have atleast 1 save file
        if len(save_sav_list) < 1:
            print("No saves found in save folder")
            savedir = None
            save_dir_List = []
            save_sav_list = []
            continue

    selected = False
    print("2. Select save directories to copy from and copy to")
    while not selected:
        # Print index and world name for user to select
        printList(save_dir_List)

        # Allow user to select their world to copy from
        selection = getNumberSelection(save_dir_List, 0)
        dir_from_to = [save_dir_List[selection]]

        # Allow user to select their world to copy to
        printList(save_dir_List)
        selection = getNumberSelection(save_dir_List, 1)
        dir_from_to.append(save_dir_List[selection])

        str = "Are you sure these are correct? {} copied to {}?".format(
            os.path.basename(dir_from_to[0]), os.path.basename(dir_from_to[1])
        )
        selection = getYNSelection(str)
        selected = selection

    print("\n3. Select overmap tiles to move\n")
    print("Please enter a coordinate to copy from")
    print('Enter coordinates in the form: "LEVEL, XCOORD1, XCOORD2, YCOORD1, YCOORD2"')
    print('Include ","\'s')
    print('Example"0,-1,2,-3,4"')
    print('Please type "n" to close\n')

    coordinate_fuples = []
    while True:
        while True:
            selection = getCDDAOvermapCoordSelection(
                "please select overmap coordinate to copy from in 1st map:"
            )
            if selection:
                print(selection)
                answer = getYNSelection("Is this correct?")
                if answer:
                    coordinate_fuples.append(selection)
                    break
                continue
            else:
                print("Coordinates not entered, closing...")
                return

        while True:
            selection = getCDDAOvermapCoordSelection(
                "4. Select overmap coordinate to replace in 2nd map:"
            )
            if selection:
                print(selection)
                answer = getYNSelection("Is this correct?")
                if answer:
                    coordinate_fuples.append(selection)
                    break
                continue
            else:
                print("Coordinates not entered, closing...")
                return

        fuples_equal = True
        for i in range(5):
            if coordinate_fuples[0][i] != coordinate_fuples[1][i]:
                fuples_equal = False
                break

        if fuples_equal:
            print("Coordinates cannot be equal, please retry")
            continue

        break

    print("Apply this copy/paste?")
    str = "copy {} from {} to {} in {}?".format(
        coordinate_fuples[0],
        os.path.basename(dir_from_to[0]),
        coordinate_fuples[1],
        os.path.basename(dir_from_to[1]),
    )
    selection = getYNSelection(str)
    if not selection:
        return

    print("copying map file...")
    from_map_file = getMapFileFromCoordinate(dir_from_to[0], coordinate_fuples[0])
    to_map_file = getMapFileFromCoordinate(dir_from_to[1], coordinate_fuples[1])

    print(dir_from_to[0])
    print(to_map_file)

    try:
        from_data = readMapFile(from_map_file)
        if not from_data:
            raise Exception("Error reading from 1st save file")

        to_data = readMapFile(to_map_file)
        if not to_data:
            raise Exception("Error reading from 2nd save file")

        for i in range(4):
            from_data[i]["coordinates"] = to_data[i]["coordinates"]
            from_data[i]["turn_last_touched"] = to_data[i]["turn_last_touched"]
            from_data[i]["temperature"] = to_data[i]["temperature"]

        writeMapFile(to_map_file, from_data)
        print("The coordinates have been copied successfully")
    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            print(e)

    return


# get directories in the save folder
def getDirs(save_path):
    save_dirs = []
    for folder in os.listdir(save_path):
        d = os.path.join(save_path, folder)
        if os.path.isdir(d):
            save_dirs.append(d)

    # Check if there are even any save files here
    if len(save_dirs) == 0:
        return []
    return save_dirs


# check if we have the save file for this directory0
def getSave(save_directory):
    for file in os.listdir(save_directory):
        f = os.path.join(save_directory, file)

        if os.path.isfile(f) and f.endswith(".sav"):
            return f
    return None


def printList(save_list):
    for index, dir in enumerate(save_list):
        print("{}. World: {}".format(index, os.path.basename(dir)))


def getNumberSelection(save_dir_List, move):
    while True:
        str = f"Please type the number of the world to copy {'to' if move == 1 else 'from'}: "
        selection = input(str)
        if not selection.isnumeric():
            print("Not a number")
            selection = None
            continue

        selection = int(selection)
        if selection < 0 or selection > (len(save_dir_List) - 1):
            print("Number not in bounds")
            selection = None
            continue
        return selection


def getYNSelection(strInputQuestion):
    while True:
        selection = input(strInputQuestion + " (Y/N): ")
        selection = selection.lower()
        if selection == "y" or selection == "n":
            return True if selection == "y" else False
        print("Not (Y/N)")
        selection = None


def getCDDAOvermapCoordSelection(str):
    while True:
        if str:
            print(str)
        selection = input("Enter coords: ")
        if selection == "n":
            return None

        selection = selection.split(",")

        retry = False
        for i in range(5):
            if not check_number(selection[i]):
                print("Value {} not an integer".format(i))
                retry = True
                break
            selection[i] = int(selection[i])

            if i == 2 or i == 4:
                if selection[i] < 0 or selection[i] >= 180:
                    print("Value {} not in bound [0,179]".format(i))
                    retry = True
                    break

            if i == 0:
                if selection[0] < -10 or selection[0] > 10:
                    print("Value {} not in bound [-10,10]".format(i))
                    retry = True
                    break

        if retry:
            continue

        return selection


def check_number(num):
    while True:
        try:
            num = int(num)
            return True
        except ValueError:
            return False


def readMapFile(mapFile):
    try:
        with open(mapFile, "r", encoding="utf8") as file:
            data = json.load(file)
            return data

    except FileNotFoundError:
        print("Map file not found...")
        return None

    except json.JSONDecodeError:
        print("JSON didn't decode correctly")
        return None

    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            print(e)

    return None


def writeMapFile(mapFile, data):
    try:
        with open(mapFile, "w") as file:
            json.dump(data, file)
            return True

    except Exception:
        print("Generic exception")
        return None

    return None


def getMapFileFromCoordinate(dir, coordinate):
    mapsFolder = os.path.join(dir, "maps")
    map32Folder = convertCoordTo32(coordinate)

    coordinateFolderStr = (
        str(map32Folder[0]) + "." + str(map32Folder[1]) + "." + str(map32Folder[2])
    )
    coordinateFolder = os.path.join(mapsFolder, coordinateFolderStr)

    mapFileCoord = convertCoordToThree(coordinate)
    mapFileStr = (
        str(mapFileCoord[0]) + "." + str(mapFileCoord[1]) + "." + str(mapFileCoord[2])
    ) + ".map"
    mapFile = os.path.join(coordinateFolder, (mapFileStr))

    return mapFile


def convertCoordToThree(coordinate):
    xcoordTotal = 0
    if coordinate[1] >= 0:
        xcoordTotal = (coordinate[1] * 180) + coordinate[2]
    else:
        xcoordTotal = ((coordinate[1] + 1) * 180) - (180 - coordinate[2])

    ycoordTotal = 0
    if coordinate[3] >= 0:
        ycoordTotal = (coordinate[3] * 180) + coordinate[4]
    else:
        ycoordTotal = ((coordinate[3] + 1) * 180) - (180 - coordinate[4])

    return [xcoordTotal, ycoordTotal, coordinate[0]]


def convertCoordTo32(coordinate):
    threeCoord = convertCoordToThree(coordinate)

    if threeCoord[0] >= 0:
        threeCoord[0] = math.floor(threeCoord[0] / 32)
    else:
        threeCoord[0] = (-math.floor(abs(threeCoord[0]) / 32)) - 1

    if threeCoord[1] >= 0:
        threeCoord[1] = math.floor(threeCoord[1] / 32)
    else:
        threeCoord[1] = (-math.floor(abs(threeCoord[1]) / 32)) - 1

    return [threeCoord[0], threeCoord[1], threeCoord[2]]


if __name__ == "__main__":
    main()


# each OM tile is 24x24 (0-23)
# negative is (-24, -1)

# each OM chunk is 180x180 (0-179)
# the coordinates in .map file are individual tiles/12 (4 submaps per OM tile)

# player location from .sav file is individual tiles from origin (0,0)
