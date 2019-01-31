# Linux Dictionary

The sources of The Linux Dictionary course avaiable on:
 * [Memrise.com](https://www.memrise.com/course/2175263/linux-dictionary/)
 * [Supermemo.com](https://www.supermemo.com/en/course/linux_dictionary)
 * [AnkiWeb.net](https://ankiweb.net/shared/info/928166313)
 * [Moodle](http://elf2.pk.edu.pl/mod/glossary/view.php?id=68717) (avaiable only
 for the students of The Cracow University of Technology)

## Generating the TSV and XML versions

Script `generate.py` generates the TSV and XML files from the given XLSX file.
If no `-o` option has been passed the files will be generated in the CWD.
The line ending sequence is OS-dependent. If the encoding of the XLSX file is
not UTF-8 the behaviour is undefined.

### Expected spreadsheet schema

 * Only the first sheet in the given file will be parsed and coverted.
 * Each row contains the phrase, definition and aliases in the following format:

   |   PHRASE   |   DEFINITON   |   [alias1]   |   [alias2]   |   [...]   |
   |:----------:|:-------------:|:------------:|:------------:|:---------:|
   | **PHRASE** | **DEFINITON** | **[alias1]** | **[alias2]** | **[...]** |
   | **[...]**  |   **[...]**   |   **[...]**  |   **[...]**  | **[...]** |

 * The sheet can containt empty rows between non-empty rows. A row will be
   omitted if it has the first cell empty.
 * The script will print warning for each phrase that occurs more than once as
   well as all definitions associated with that phrase.

### Usage

The script requires the `xlrd` python3 module. To install it simply run:
```bash
  $ [sudo] pip3 install xlrd  # with admin/root privileges
  $ pip3 install --user xlrd  # without admin/root privileges
```

To generate the TSV and XML files run:
```bash
  $ python3 generate.py [-o output_dir] path_to_excel_file.xlsx
```

You can add `-w` flag to activate the watch mode. The script will generate files
automatically every time when the XLSX file has been changed.
```bash
  $ python3 generate.py -w [-o output_dir] path_to_excel_file.xlsx
```

