.PHONY: all clean
all:
	latexmk -r .latexmkrc src/main.tex

clean:
	latexmk -r .latexmkrc -c src/main.tex
