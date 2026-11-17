.PHONY: all clean
all:
	latexmk -r .latexmkrc src/main.tex

clean:
	latexmk -r .latexmkrc -c src/main.tex

.PHONY: figures
figures:
	python3 misc/build-figures.py
