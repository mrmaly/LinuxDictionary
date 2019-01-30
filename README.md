# Linux Dictionary

The sources of The Linux Dictionary course avaiable on:
 * [Memrise.com](https://www.memrise.com/course/2175263/linux-dictionary/)
 * [Supermemo.com](https://www.supermemo.com/en/course/linux_dictionary)
 * [AnkiWeb.net](https://ankiweb.net/shared/info/928166313)

## Generating the TSV and XML versions

Script `generate.py` generates the TSV and XML files from the given XLSX file.
If no `-o` option has been passed the files are generated in the CWD.
The line ending sequence is OS-dependent. If the encoding of the XLSX file is
not UTF-8 the behaviour is undefined.

### Usage

The script requires the `xlrd` python3 module. To install it simply run:
```bash
  # pip3 install xlrd         # with admin/root privileges
  $ pip3 install --user xlrd  # without admin/root privileges
```

To generate the TSV and XML files run:
```bash
  $ python3 generate.py [-o output_dir] path_to_excel_file.xlsx
```

