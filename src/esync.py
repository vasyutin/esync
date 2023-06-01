import sys
import argparse
import datetime
import os
import bisect
import shutil
from stat import S_ISREG, S_ISDIR
from time import sleep

g_FatMode = None

# -----------------------------------------------------------------------------
def GetFolderState(Folder_, Files_, Dirs_):
	def ProcessFolder(Folder_, CleanFolder_):
		for Item in os.scandir(Folder_):
			Status = Item.stat()
			if S_ISDIR(Status.st_mode):
				Dirs_.append(CleanFolder_ + Item.name)
				ProcessFolder(Item.path, CleanFolder_ + Item.name + os.sep)
			elif S_ISREG(Status.st_mode):
				MTime = Status.st_mtime
				if g_FatMode:
					TimeInt = (int(MTime) >> 1) << 1
					TimeBase = float(TimeInt)
					TimeDiff = MTime - TimeBase
					if TimeDiff > 1.0:
						MTime = TimeBase + 2.0
					else:
						MTime = TimeBase
				Files_.append([CleanFolder_ + Item.name, MTime, Status.st_size])
   #
	ProcessFolder(Folder_, '')
	Dirs_.sort()
	Files_.sort(key=lambda x: x[0])
	return True

# -----------------------------------------------------------------------------
g_MinFolderTime = None

def ModificationTime(Folder_):
	def MtProcessFolder(Folder_):
		global g_MinFolderTime

		for Item in os.scandir(Folder_):
			Status = Item.stat()
			if S_ISDIR(Status.st_mode):
				MtProcessFolder(Item.path)
			elif S_ISREG(Status.st_mode):
				if g_MinFolderTime == None:
					g_MinFolderTime = Status.st_mtime
				else:
					if Status.st_mtime > g_MinFolderTime:
						g_MinFolderTime = Status.st_mtime
   #
	MtProcessFolder(Folder_)
	if g_MinFolderTime == None:
		print("Directory '{}' is empty (has no files).".format(Folder_))
	else:
		print('Modification time is ' + (datetime.datetime.fromtimestamp(g_MinFolderTime)).strftime('%Y-%m-%d %H:%M:%S') + '.')
	return 0

# -----------------------------------------------------------------------------
if __name__ != '__main__':
    sys.exit(1)

ArgParser = argparse.ArgumentParser(description='ESync 1.3. Synchronizes directories (see https://github.com/vasyutin/esync).')
ArgParser.add_argument('-s', '--source', type = str, help = 'Source directory.', dest = 'source')
ArgParser.add_argument('-d', '--destination', type = str, help = 'Destination directory.', dest = 'destination')
ArgParser.add_argument('-v', '--verbose', action='store_true', help = "Print actions' information.", default = False, \
	dest='verbose')
ArgParser.add_argument('-r', '--dry-run', action='store_true', help = 'Show actions to be taken but do not perform sync.', \
	default = False, dest='dry')
ArgParser.add_argument('-o', '--overwrite-newer', action='store_true', \
	help = 'Enables sync if some files in the destination directory are newer than the same files in the source directory.', default = False, \
	dest='overwrite_newer')
ArgParser.add_argument('-f', '--fat', action='store_true', \
	help = 'Round time to 2 seconds so program can synchronize normally files on FAT/FAT32/ExFAT.', default = False, \
	dest='fat')
ArgParser.add_argument('-m', '--modified', type = str, help = 'Print the time when the files in the given folder were last modified.', dest = 'modified')

Arguments = ArgParser.parse_args()

Verbose = True if Arguments.dry else Arguments.verbose
g_FatMode = Arguments.fat

if Arguments.modified:
	if Arguments.source != None:
		print("Error! The source directory option (-s/--source) can't be used with -m (--modified) option.", file = sys.stderr)
		ArgParser.print_help()
		sys.exit(1)
	if Arguments.destination != None:
		print("Error! destination directory option (-d/--destination) can't be used with -m (--modified) option.", file = sys.stderr)
		ArgParser.print_help()
		sys.exit(1)
	sys.exit(ModificationTime(Arguments.modified))

if Arguments.source == None or Arguments.destination == None:
	print('Error! No source and/or destination directory is specified.', file = sys.stderr)
	ArgParser.print_help()
	sys.exit(1)

if not os.path.isdir(Arguments.source):
	print('Error! Directory "' + Arguments.source + '" not exists.', file = sys.stderr)
	sys.exit(1)

SourcePath = os.path.normpath(Arguments.source)
if not SourcePath.endswith(os.sep):
	SourcePath += os.sep

DestPath = os.path.normpath(Arguments.destination)
if not DestPath.endswith(os.sep):
	DestPath += os.sep

SourceFiles = []
SourceDirs = []
try:
	GetFolderState(SourcePath, SourceFiles, SourceDirs)
except:
	print('Error! Error reading directory "' + Arguments.source + '".', file = sys.stderr)
	sys.exit(1)

#print('\n\nSourceDirs\n--------------')
#for Str in SourceDirs:
#	print(Str)
#print('\n\nSourceFiles\n--------------')
#for Str in SourceFiles:
#	print(Str)

DestFiles = []
DestDirs = []
if os.path.isdir(DestPath):
	try:
		GetFolderState(DestPath, DestFiles, DestDirs)
	except:
		print('Error! Error reading directory "' + Arguments.destination + '".', file = sys.stderr)
		sys.exit(1)

#print('\n\nDestDirs\n--------------')
#for Str in DestDirs:
#	print(Str)
#print('\n\nDestFiles\n--------------')
#for Str in DestFiles:
#	print(Str)

#print(SourceFiles)
#print(SourceDirs)
#print(DestFiles)
#print(DestDirs)

if not Arguments.overwrite_newer and len(DestFiles):
	NewerFiles = []
	for i in range(len(SourceFiles)):
		FileName = SourceFiles[i][0]
		Pos = bisect.bisect_left(DestFiles, FileName, key=lambda x: x[0])
		if Pos > (len(DestFiles) - 1) or DestFiles[Pos][0] != FileName:
			continue
		if SourceFiles[i][1] < DestFiles[Pos][1]:
			NewerFiles.append(FileName)
	if len(NewerFiles):
		print('WARNING! Sync is not performed because these files in the destination directory are newer than the same files in the source directory:', \
			file = sys.stderr)
		Counter = 1
		for FileName in NewerFiles:
			print("\t" + str(Counter) + ") '" + DestPath + FileName + "' is newer than '" + SourcePath + FileName + "'")
			Counter += 1
		print("\nERROR! Sync is not performed. Use '-o' option to overwrite newer files.")
		sys.exit(1)

if os.path.isdir(DestPath):
	# Delete files not present in the source directory, files older than files in the source directory, 
	# or files which sizes has changed
	for i in range(len(DestFiles)):
		FileName = DestFiles[i][0]
		Pos = bisect.bisect_left(SourceFiles, FileName, key=lambda x: x[0])
		if Pos > (len(SourceFiles) - 1) or SourceFiles[Pos][0] != FileName or DestFiles[i][1] != SourceFiles[Pos][1] or \
			DestFiles[i][2] != SourceFiles[Pos][2]:
			if Verbose:
				print('deleting ' + DestPath + FileName)
			if not Arguments.dry:
				try:
					os.remove(DestPath + FileName)
				except:
					# Make second attempt to delete file (helps sometimes with network FS)
					sleep(0.01)
					try:
						os.remove(DestPath + FileName)
					except:
						print('ERROR deleting file ' + DestPath + FileName + '.', file = sys.stderr)
						sys.exit(1)

	DirsToDelete = []
	for DirName in DestDirs:
		Pos = bisect.bisect_left(SourceDirs, DirName)
		if Pos > (len(SourceDirs) - 1) or SourceDirs[Pos] != DirName:
			DirsToDelete.append(DestPath + DirName)

	DirsToDelete.sort(key=lambda x: len(x))
	for DirName in reversed(DirsToDelete):
		if Verbose:
			print('deleting ' + DirName + os.sep)
		if not Arguments.dry:
			try:
				os.rmdir(DirName)
			except:
				print('ERROR deleting directory ' + DestPath + DirName + '.', file = sys.stderr)
				sys.exit(1)
else:
	if Verbose:
		print('creating ' + DestPath)
	if not Arguments.dry:
		try:
			os.makedirs(DestPath)
		except:
			print('ERROR creating directory ' + DestPath + '.', file = sys.stderr)
			sys.exit(1)

# Create dirs
DirsToCreate = []
for DirName in SourceDirs:
	Pos = bisect.bisect_left(DestDirs, DirName)
	if Pos > (len(DestDirs) - 1) or DestDirs[Pos] != DirName:
		DirsToCreate.append(DestPath + DirName)

DirsToCreate.sort(key=lambda x: len(x))
for DirName in DirsToCreate:
	if Verbose:
		print('creating ' + DirName + os.sep)
	if not Arguments.dry:
		try:
			os.mkdir(DirName)
		except:
			print('ERROR creating directory ' + DirName + '.', file = sys.stderr)
			sys.exit(1)

#Copy files
for i in range(len(SourceFiles)):
	FileName = SourceFiles[i][0]
	Pos = bisect.bisect_left(DestFiles, FileName, key=lambda x: x[0])
	if Pos > (len(DestFiles) - 1) or DestFiles[Pos][0] != FileName or DestFiles[Pos][1] != SourceFiles[i][1] or \
		DestFiles[Pos][2] != SourceFiles[i][2]:
		if Verbose:
			print('copying ' + SourcePath + FileName)
		if not Arguments.dry:
			if g_FatMode:
				try:
					shutil.copy(SourcePath + FileName, DestPath + FileName)
				except Exception as E_:
					print('ERROR copying file ' + SourcePath + FileName + ': ' + str(E_), file = sys.stderr)
					sys.exit(1)

				ModTime = SourceFiles[i][1]
				try:
					os.utime(DestPath + FileName, (ModTime, ModTime))
				except Exception as E_:
					print('ERROR changing file\'s time ' + SourcePath + FileName + ': ' + str(E_), file = sys.stderr)
					sys.exit(1)

			else: # Fat mode
				try:
					shutil.copy2(SourcePath + FileName, DestPath + FileName)
				except Exception as E_:
					print('ERROR copying file ' + SourcePath + FileName + ': ' + str(E_), file = sys.stderr)
					sys.exit(1)

sys.exit(0)