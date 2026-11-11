.PHONY: all clean
all:
	latexmk -r .latexmkrc -outdir=../build src/main.tex

clean:
	latexmk -r .latexmkrc -outdir=../build -c src/main.tex
