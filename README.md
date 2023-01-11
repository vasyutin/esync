# ESYNC

Synchronizes directories. Allows to take into account rounding up to 2 seconds in FAT/FAT32/ExFAT during synchronization.

# Usage
```
esync [-h] [-s SOURCE] [-d DESTINATION] [-v] [-r] [-w] [-f] [-m MODIFIED]

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        Source directory.
  -d DESTINATION, --destination DESTINATION
                        Destination directory.
  -v, --verbose         Print actions' information.
  -r, --dry-run         Show actions to be taken but do not perform sync.
  -w, --warn            Warn and stop sync if some files in the destination
                        directory are newer than the same files in the source
                        directory.
  -f, --fat             Round time to 2 seconds so program can synchronize
                        normally files on FAT/FAT32/ExFAT.
  -m MODIFIED, --modified MODIFIED
                        Print the time when the files in the given folder were
                        last modified.
```