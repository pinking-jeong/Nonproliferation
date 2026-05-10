# Makefile for the OS-PM system paper.
# Targets:
#   make         — build PDF via latexmk + xelatex
#   make clean   — remove build artifacts
#   make watch   — continuous rebuild on save (latexmk -pvc)

PAPER = main
TEX   = $(PAPER).tex
BIB   = references.bib
LATEXMK = latexmk -pdf -xelatex -interaction=nonstopmode -halt-on-error

.PHONY: all clean watch

all: $(PAPER).pdf

$(PAPER).pdf: $(TEX) $(BIB)
	$(LATEXMK) $(TEX)

watch:
	$(LATEXMK) -pvc $(TEX)

clean:
	latexmk -C
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk *.synctex.gz
