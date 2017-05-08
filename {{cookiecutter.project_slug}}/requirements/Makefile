
all: base.txt dev.txt test.txt

base.txt: base.in
	pip-compile base.in --output-file base.txt

dev.txt: dev.in base.in
	pip-compile dev.in --output-file dev.txt

test.txt: test.in base.in
	pip-compile test.in --output-file test.txt
