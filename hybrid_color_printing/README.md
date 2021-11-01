# hybrid_color_printing.py

Simple python script that lists color and b/w pages in a PDF. Might help you save cost, paper and toner for large docs
like dissertations or datasheets, where you might not want to print all 240 pages in color for just those 20 color pages
in the pdf file.

Script uses Ghostscript (>9.5) and it's inkcov device, which outputs C, M, Y, K values of each page. Till a better 
method is found, page is sorted as B/W if C, M, Y, K values are zero or same. 

### Ghostscript Setup
Ghostscript 9.55 or better is required and it's executable must be in `$PATH`.

1. Download your OS specific installation file of Ghostscript from https://www.ghostscript.com/releases/gsdnld.html
2. Install by running executable
3. Add the location of the installed executable to `$PATH`. For Windows, go to Control Panel, search 'Environment
   Variables'. In 'Advanced' tab of the dialogue box, click on 'Environment Variables'. Under System variables, find and
   select Path, Edit, New and Browse to directory where Ghostscript is installed, for e.g. 
   `C:\Program Files\gs\gs9.55.0\bin\`
   
### Usage

`hybrid_color_printing.py file.pdf`

By default, output is list of color and b/w pages in ranged list format (e.g. 1-7,13,14,34-65).

`hybrid_color_printing.py file.pdf -F`

Use -F for expanded list output. (e.g. 1,2,3,4,5,6,7,13,14,34,35,36,....,65)

`hybrid_color_printing.py file.pdf -DS`

For printing back to back or double sided, use `-DS` option. It pairs and combines the required pages (for example, if 
17 and 36 are color pages, you need to input 17,18 and 35,36 to print double sided consistently).

`hybrid_color_printing.py file.pdf -DS -B 0.05 -C 0.5`

use -B cost_per_blackpage and -C cost_per_colorpage if total cost of printing is needed.





