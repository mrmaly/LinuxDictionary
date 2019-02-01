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
The line ending sequence in the generated files is OS-dependent.

### Expected spreadsheet schema

 * The script will generate files for each sheet in the XLSX file, as well as
   files containing merged content of all sheets.
 * The file has to be UTF-8 encoded. If it's not the behaviour is undefined.
 * Each non-empty row has to contain a phrase, definition and aliases in the
   following format:

   |   PHRASE   |   DEFINITON   |   [alias1]   |   [alias2]   |   [...]   |
   |:----------:|:-------------:|:------------:|:------------:|:---------:|
   | **PHRASE** | **DEFINITON** | **[alias1]** | **[alias2]** | **[...]** |
   | **[...]**  |   **[...]**   |   **[...]**  |   **[...]**  | **[...]** |

 * A sheet can contain empty rows between non-empty rows. A row will be omitted
   if it has the first cell empty.
 * The script will print warning for each phrase that occurs more than once
   (case insensitive), as well as all definitions associated with that phrase.

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

#### The watch mode

You can add `-w` flag to activate the watch mode. The script will generate files
automatically every time when the XLSX file has been changed. The file is
checked for changes every 0.5 second.
```bash
  $ python3 generate.py -w [-o output_dir] path_to_excel_file.xlsx
```

To change the interval between checks add a new value (in seconds) after the
`-w` flag (now it's a option though).
```bash
  $ python3 generate.py -w 1.337 [-o output_dir] path_to_excel_file.xlsx
```

#### The simple mode
To prevent the script from generating files for each sheet add `-s` flag. Only
files with merged content will be generated. Useful if you're not going to
create Memrise levels.
```bash
  $ python3 generate.py -s [-o output_dir] path_to_excel_file.xlsx
```

#### The metadata file

You can specify a metadata JSON file via `-m` option. If no metadata file has
been given, the meta tags in the XML file will be filled with placeholders.
```bash
  $ python3 generate.py -m ./metadata.json [-o output_dir] path_to_excel_file.xlsx
```

The JSON file has to have the following format:
```json
{
  "name": "<project_name>",
  "short_description": "<description>"
}
```
