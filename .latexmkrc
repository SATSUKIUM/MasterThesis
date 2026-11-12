$latex = 'platex -kanji=utf8 -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$bibtex = 'pbibtex %O %B';
$dvipdf = 'dvipdfmx %O -o %D %S';
$pdf_mode = 3;
$max_repeat = 5;
$do_cd = 1;

# ソースの場所によらずリポジトリ直下の out/ に出力する。
use File::Basename qw(dirname);
use Cwd qw(abs_path);
$out_dir = dirname(abs_path(__FILE__)) . '/out';
