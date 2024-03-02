# What is ESync

ESync is a command-line utility designed to synchronize directories between a source and a destination. It provides a set of options that allow users to specify source and destination directories, control the synchronization process, and obtain detailed information about the synchronization actions. Notably, the program provides functionality to accommodate the rounding up to 2 seconds in FAT/FAT32/ExFAT file systems during synchronization.

# Usage

The program can be executed using the `esync` executable with the following command-line options:

```
esync [-h] [-s SOURCE] [-d DESTINATION] [-v] [-r] [-o] [-f] [-m FOLDER]
```

Options:

- `-h, --help`: Show the help message and exit.
- `-s SOURCE, --source SOURCE`: Specify the source directory for synchronization.
- `-d DESTINATION, --destination DESTINATION`: Specify the destination directory for synchronization.
- `-v, --verbose`: Enable verbose mode to print detailed actions' information during synchronization.
- `-r, --dry-run`: Perform a dry run to display the actions to be taken, but do not execute the synchronization.
- `-o, --overwrite-newer`: Enable synchronization even if some files in the destination directory are newer than the corresponding files in the source directory.
- `-f, --fat`: Round time to 2 seconds, allowing synchronization of files on FAT/FAT32/ExFAT file systems.
- `-m FOLDER, --modified FOLDER`: Print the time when the files in the given folder were last modified.

Usage Examples:

1. Synchronize directories:
   ```
   esync -s "C:\SourceDirectory" -d "D:\DestinationDirectory"
   ```

2. Perform a dry run for synchronization:
   ```
   esync -s "C:\SourceDirectory" -d "D:\DestinationDirectory" -r
   ```

3. Enable verbose mode for detailed synchronization information:
   ```
   esync -s "C:\SourceDirectory" -d "D:\DestinationDirectory" -v
   ```

4. Synchronize, even if destination files are newer:
   ```
   esync -s "C:\SourceDirectory" -d "D:\DestinationDirectory" -o
   ```

The ESync program provides users with a powerful and flexible tool for synchronizing directories, allowing for efficient management and maintenance of file and folder contents across different storage locations. The program's support for rounding up to 2 seconds in FAT/FAT32/ExFAT file systems during synchronization ensures compatibility and reliability when working with these file systems. Users can utilize its features to perform various synchronization tasks and obtain detailed information about synchronization actions.

# License

GNU GPL Version 3

# Author

Sergey Vasyutin (sergey [at] vasyut.in)